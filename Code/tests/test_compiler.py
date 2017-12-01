#!/usr/bin/env python

import pytest

import os
import subprocess
import sys

#import enum

import argparse
import re

### Constants

this_file = os.path.realpath(__file__)
this_dir = os.path.dirname(this_file)
root_dir = os.path.realpath(os.path.join(this_dir, '..'))

python_exe = sys.executable

pyyc = os.path.join(root_dir, 'pyyc')

runtime_dir = os.path.join(root_dir, 'runtime')
runtime_lib = os.path.join(runtime_dir, 'libpyyruntime.a')

cc = ['gcc','-m32','-g','-lm']

default_pyyctests = os.path.join(this_dir, 'resources')
default_outof = 100

### Code

#Result = enum.Enum('Result', 'success warning failure')
class Result:
    success = 0
    warning = 1
    failure = 2

def popen_result(popen):
    # type: (Popen) -> Result
    (out, err) = popen.communicate()
    retcode = popen.wait()
    if retcode != 0:
        if not (out is None):
            print out
        return Result.failure
    elif err: # stderr is not empty or None
        return Result.warning
    else:
        return Result.success

class Pyyctest:
    def __init__(self, test_py):
        if not os.path.exists(test_py):
            raise ValueError('Test file {} does not exist'.format(test_py))
        base = self.base_of_testname(test_py)
        if base is None:
            raise ValueError('Test file must have a .py extension')
        self.base = base
        self.pysource = base + '.py'
        self.starget = base + '.s'
        self.compileout = base + '.compileout'
        self.compileerr = base + '.compileerr'
        self.exe = base
        self.output = base + '.out'
        self.input = base + '.in'
        self.expected = base + '.expected'

    @staticmethod
    def base_of_testname(test_py):
        # type: (str) -> Optional[str]
        (base, ext) = os.path.splitext(test_py)
        return base if ext == '.py' else None

    @staticmethod
    def build_runtime():
        popen = subprocess.Popen(['make', '-C', runtime_dir], stdout=subprocess.PIPE)
        return popen_result(popen)

    @staticmethod
    def build_compiler():
        popen = subprocess.Popen(['make', '-C', root_dir], stdout=subprocess.PIPE)
        return popen_result(popen)

    def compile(self):
        # type: () -> Result
        with open(self.compileout, 'w') as outfile:
            with open(self.compileerr, 'w') as errfile:
                popen = subprocess.Popen(['bash', pyyc, self.pysource],
                                         stdout=outfile, stderr=errfile)
        return popen_result(popen)

    def link(self):
        # type: () -> Result
        popen = subprocess.Popen(cc + [self.starget, runtime_lib, '-o', self.exe],
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return popen_result(popen)

    def run(self, exe, outfilename):
        # type: (, List[str], str) -> Result
        with open(outfilename, 'w') as outfile:
            if os.path.exists(self.input):
                with open(self.input, 'r') as infile:
                    popen = subprocess.Popen(exe, stdin=infile, stdout=outfile)
            else:
                popen = subprocess.Popen(exe, stdout=outfile)
            return popen_result(popen)

    def run_exe(self):
        # type: () -> Result
        return self.run([self.exe], self.output)

    def run_python(self):
        # type: () -> Result
        return self.run([python_exe, self.pysource], self.expected)

    def diff_with_python(self):
        # type: () -> Result
        popen = subprocess.Popen(['diff', '-w', '-B', '-u', self.expected, self.output],
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return popen_result(popen)

def test_compiler(filename_py):
    # type: (str) -> None
    try:
        pyyctest = Pyyctest(filename_py)
        if pyyctest.run_python() == Result.failure:
            raise ValueError('Test file {} not valid'.format(filename_py))
    except ValueError as err:
        pytest.skip(err.message)
    assert pyyctest.compile() != Result.failure
    assert pyyctest.link() != Result.failure
    assert pyyctest.run_exe() != Result.failure
    assert pyyctest.diff_with_python() != Result.failure

### Cog Autograding Interface

def extract_failpass(log):
    """Extracts the failed and passed tests for the COG autograding interface.

    Todo: Extracting from the expected output string is likely brittle.
    """
    # type: (str) -> Optional[(int,int)]
    def extract(pattern):
        match = re.search(pattern, log)
        return int(match.group(1)) if not (match is None) else 0
    return (extract(r'(\d+) failed'), extract(r'(\d+) passed'))

def autograde_cog(args):
    popen = subprocess.Popen([python_exe, '-m', 'pytest', this_file, '--pyyctests', args.pyyctests],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (out, err) = popen.communicate()
    print >> sys.stderr, out
    print >> sys.stderr, err
    (nfail, npass) = extract_failpass(out)
    if nfail == 0 and npass == 0:
        print >> sys.stderr, 'Error extracting score!'
        return 1
    else:
        ntotal = nfail + npass
        print '{:.4f}'.format((npass / (ntotal * 1.0)) * args.outof)
        return popen.wait()

### Main

def main(argv):
    argparser = argparse.ArgumentParser(description='Test or autograde pyyc compilers.')
    subparsers = argparser.add_subparsers()

    test_parser = subparsers.add_parser('test', help='run pytest')
    def test_cmd(_, xargs):
        return pytest.main(sys.argv[0] + xargs)
    test_parser.set_defaults(cmd=test_cmd)

    grade_parser = subparsers.add_parser('grade', help='run with autograder interface')
    grade_parser.add_argument('--outof',
                              help='compute score out of N (default: {})'.format(default_outof),
                              metavar='N',
                              type=int,
                              default=default_outof)
    grade_parser.add_argument('--grader',
                              help='grader interface',
                              choices=['cog'],
                              required=True)
    grade_parser.add_argument('--pyyctests',
                              help='pyyc test file name or root directory (default: {})'.format(default_pyyctests),
                              default=default_pyyctests)
    def grade_cmd(args, _):
        if args.grader == 'cog':
            return autograde_cog(args)
        else:
            raise ValueError('gremlins: unspecified args.grader')
    grade_parser.set_defaults(cmd=grade_cmd)

    (args, xargs) = argparser.parse_known_args(argv[1:])
    return args.cmd(args, xargs)

if __name__ == '__main__':
    exit(main(sys.argv))

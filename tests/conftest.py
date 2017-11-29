import pytest

import os

from test_compiler import Pyyctest, Result, default_pyyctests

### Code

def find_pyyctests(root):
    # type: (str) -> List[str]
    acc = []
    def loop(root):
        # type: (str) -> List[str]
        if os.path.isfile(root):
            if Pyyctest.base_of_testname(root) != None:
                acc.append(root)
        elif os.path.isdir(root):
            for sub in os.listdir(root):
                loop(os.path.join(root,sub))
    loop(root)
    return acc

@pytest.fixture
def filename_py(request):
    runtime_result = Pyyctest.build_runtime()
    if runtime_result == Result.failure:
        print 'Failed to build the run-time system.'
        yield None
    compiler_result = Pyyctest.build_compiler()
    if compiler_result == Result.failure:
        print 'Failed to build your compiler.'
        yield None
    yield request.param

def pytest_addoption(parser):
    parser.addoption('--pyyctests',
                     help='pyyc test file name or root directory (default: {})'.format(default_pyyctests))

def pytest_generate_tests(metafunc):
    if 'filename_py' in metafunc.fixturenames:
        option = metafunc.config.getoption('pyyctests')
        if option is None:
            abspath = default_pyyctests
        else:
            abspath = option if os.path.isabs(option) else os.path.abspath(option)
            abspath = os.path.realpath(abspath)
            if not os.path.exists(abspath):
                raise ValueError('Test path {} does not exist.'.format(abspath))
        metafunc.parametrize('filename_py', find_pyyctests(abspath), indirect=True)
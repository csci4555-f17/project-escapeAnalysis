# Compiler Construction Labs

This repository is for the lab projects in CSCI 4555/5525 and ECEN 4553/5523 Compiler Construction at the University of Colorado Boulder.

As an advanced course, these labs are designed to be open ended with a significant flexibility for your design. There is a minimal amount of starter files in this repository: a minimal run-time system for your programs, a wrapper script for your compiler `pyyc`, and a `Makefile` for your convenience. You are free to use or ignore any of these files.

Your compiler should take one argument for the name of the input Python `.py` file to compile, and it should produce an output x86 assembly file with the same name as the input file except that the `.py` suffix has been replaced by the `.s` suffix.

Edit the wrapper script `pyyc` as appropriate. If your compiler `main` is at `src/pyyc/compile.py`, then you won't need to edit this script.

Also for your convenience, the tester used in the autograder is provided for you for your own testing. To use the tester, do something like the following:

```bash
$ pytest --pyyctests mytests
```

where `mytests` is the directory with your compiler tests. Make sure you have [pytest] installed. You might want to consider using [pipenv] to manage your dependencies and Python environment.

Then, to run a program compiled from your compiler. You need to do something like the following, which is the sequence that the autotester follows:

- Build the run-time system (if it is not already built).
```bash
$ make -C runtime
```

- Build your compiler (if necessary). You may modify the `Makefile` as necessary to build your compiler.
```bash
$ make
```

- Compile the test program.
```bash
$ ./pyyc mytests/test1.py
```

- Link your assembly with the run-time system.
```bash
$ gcc -m32 -g -lm mytests/test1.s runtime/libpyyruntime.a -o mytests/test1
```

- Run your program.
```bash
$ cat mytests/test1.in | mytests/test1 > mytests/test1.out
```

- Generate the expected output.
```bash
$ cat mytests/test1.in | python mytests/test1.py > mytests/test1.expected
```

- Diff your result with the expected output.
```
$ diff -w -B -u mytests/test1.expected mytests/test1.out
```

For your convenience, the `Test.mk` makefile (included in `Makefile`) has targets for these steps that you may use, modify, or ignore as you like.

Your compiler needs to produce code that runs on an x86 Linux machine.

[pytest]: https://docs.pytest.org
[pipenv]: http://docs.pipenv.org
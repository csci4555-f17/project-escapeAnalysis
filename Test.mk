# Makefile for calling your compiler.
#
# Defines rules for invoking your wrapper pyyc script,
# linking the run-time system, and running a test input.
#
# This file should not need to be edited for your compiler (though you may).

# THIS_DIR is bound to the directory that this script file is in.
THIS_DIR=$(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))

# Location of the runtime
RUNTIME_DIR=$(THIS_DIR)/runtime
RUNTIME_LIB=$(RUNTIME_DIR)/libpyyruntime.a

# Location of the pyyc
PYYC=$(THIS_DIR)/pyyc

# Compile and link for 32-bit architecture
CC=gcc
CFLAGS=-m32 -g -lm

# Tests Root
PYYCTESTS_ROOT=$(THIS_DIR)/tests/resources
PYYCTESTS=$(shell find $(PYYCTESTS_ROOT) -type f -name '*.py')

# Python
PYTHON=python

# Create x86 assembly .s file using your compiler.
%.s: %.py
	$(PYYC) $<
	
# Create executable from your assembly .s file.
%: %.s runtime
	$(CC) $(CFLAGS) $< $(RUNTIME_LIB) -o $@
	
# Run your executable to create an output .out file given a .in input file.
%.out: %.in %
	cat $< | $* >$@

# Run Python to create an output .expected file given a .in input file.
%.expected: %.in %.py
	cat $< | $(PYTHON) ${<:%.in=%.py} >$@

# Clean up generated files from tests
.PHONY: clean-tests
clean-tests:
	rm -f $(PYYCTESTS:%.py=%.s)
	rm -f $(PYYCTESTS:%.py=%.expected)
	rm -f $(PYYCTESTS:%.py=%.compileout)
	rm -f $(PYYCTESTS:%.py=%.compileerr)
	rm -f $(PYYCTESTS:%.py=%)
	rm -f $(PYYCTESTS:%.py=%.out)
	rm -rf $(PYYCTESTS:%.py=%.dSYM)
	
# Create the run-time library if necessary.
.PHONY: runtime
runtime:
	$(MAKE) -C $(RUNTIME_DIR)
.PHONY: runtime-clean
runtime-clean:
	$(MAKE) -C $(RUNTIME_DIR) clean

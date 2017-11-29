# Makefile to build your compiler. Please edit as you like to build
# your compiler in the appropriate way.
#
# Includes the Test.mk Makefile to test using your compiler.
#
# You should edit this file so that your compiler can be built using
# the default 'all' rule:
#
# $ make
#
# And could be cleaned with the 'clean' rule:
#
# $ make clean
#

# THIS_DIR is bound to the directory that this script file is in.
# Use as needed.
THIS_DIR=$(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))

# Edit as needed to build your compiler
.PHONY: all
all: runtime

# Edit as needed to clean your build
.PHONY: clean
clean: runtime-clean

include Test.mk

# Requirements (based on ubuntu 16.04)
# apt-get install
#		python-pip
#   cmake
#
# pip install --upgrade pip
# pip install --user
#   autopep8
#   flake8
#   pylint
#   sphinx
#

mkfile_path := $(abspath $(lastword $(MAKEFILE_LIST)))
current_dir := $(notdir $(patsubst %/,%,$(dir $(mkfile_path))))

export PYTHONPATH=$(current_dir)

% : .build/Makefile
	@echo "Real build system"
	cd .build/ && env -u MAKELEVEL $(MAKE) $@
all:

test: all

.build/Makefile:
	@echo "Bootstraping build system"
	mkdir -p .build
	touch .build/CMakeCache.txt
	cd .build && env cmake -DIS_TRAVIS_CI=True ../

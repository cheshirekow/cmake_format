# Requirements (based on ubuntu 16.04)
# apt-get install
#		python-pip
#		clang
#   clang-format
#   cmake
#   gcc
#   g++
#   libfuse-dev
#
# pip install --upgrade pip
# pip install --user
# 	cpplint
#   autopep8
#   pylint
#   sphinx

% : .build/cmake_clang/Makefile \
    .build/cmake_gnu/Makefile
	@echo ""
	@echo "clang-build"
	@echo "-----------"
	cd .build/cmake_clang && env -u MAKELEVEL make $@

	@echo ""
	@echo "GNU-build"
	@echo "-----------"
	cd .build/cmake_gnu && env -u MAKELEVEL make $@

all:

test: all

.build/cmake_clang/Makefile:
	@echo ""
	@echo "Configuring clang cmake Build"
	mkdir -p .build/cmake_clang
	cd .build/cmake_clang \
    && env CC=clang CXX=clang++ cmake -DCMAKE_BUILD_TYPE=Debug ../../
	touch .build/cmake_clang/CMakeCache.txt

.build/cmake_gnu/Makefile:
	@echo ""
	@echo "Configuring GNU cmake Build"
	mkdir -p .build/cmake_gnu
	cd .build/cmake_gnu \
    && env cmake -DCMAKE_BUILD_TYPE=Debug ../../
	touch .build/cmake_gnu/CMakeCache.txt




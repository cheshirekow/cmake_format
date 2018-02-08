import io
from setuptools import setup

with io.open('README.rst', encoding='utf8') as infile:
  long_description = infile.read()

setup(
    name='cmake_format',
    packages=['cmake_format'],
    version='0.3.1',
    description="Can format your listfiles so they don't look like crap",
    long_description=long_description,
    author='Josh Bialkowski',
    author_email='josh.bialkowski@gmail.com',
    url='https://github.com/cheshirekow/cmake_format',
    download_url='https://github.com/cheshirekow/cmake_format/archive/0.2.0.tar.gz',
    keywords=['cmake', 'format'],
    classifiers=[],
    entry_points={
        'console_scripts': ['cmake-format=cmake_format.__main__:main'],
    }
)

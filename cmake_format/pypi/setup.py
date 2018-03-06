import io
from setuptools import setup

GITHUB_URL = 'https://github.com/cheshirekow/cmake_format'
VERSION = '0.3.4'

with io.open('README.rst', encoding='utf8') as infile:
  long_description = infile.read()

setup(
    name='cmake_format',
    packages=['cmake_format'],
    version=VERSION,
    description="Can format your listfiles so they don't look like crap",
    long_description=long_description,
    author='Josh Bialkowski',
    author_email='josh.bialkowski@gmail.com',
    url=GITHUB_URL,
    download_url='{}/archive/{}.tar.gz'.format(GITHUB_URL, VERSION),
    keywords=['cmake', 'format'],
    classifiers=[],
    entry_points={
        'console_scripts': ['cmake-format=cmake_format.__main__:main'],
    },
    extras_require={
        'YAML': ["pyyaml"],
    }
)

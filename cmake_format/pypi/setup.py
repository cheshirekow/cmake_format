import io
from setuptools import setup

GITHUB_URL = 'https://github.com/cheshirekow/cmake_format'

VERSION = None
with io.open('cmake_format/__init__.py', encoding='utf-8') as infile:
  for line in infile:
    line = line.strip()
    if line.startswith('VERSION ='):
      VERSION = line.split('=', 1)[1].strip().strip("'")

assert VERSION is not None


with io.open('README.rst', encoding='utf-8') as infile:
  long_description = infile.read()

setup(
    name='cmake_format',
    packages=[
        'cmake_format',
        'cmake_format.command_tests',
        'cmake_format.parse',
        'cmake_format.parse_funs',
        'cmake_lint',
    ],
    version=VERSION,
    description="Can format your listfiles so they don't look like crap",
    long_description=long_description,
    author='Josh Bialkowski',
    author_email='josh.bialkowski@gmail.com',
    url=GITHUB_URL,
    download_url='{}/archive/{}.tar.gz'.format(GITHUB_URL, VERSION),
    keywords=['cmake', 'format'],
    license="GPLv3",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)"
    ],
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'cmake-annotate=cmake_format.annotate:main',
            'cmake-format=cmake_format.__main__:main',
            'cmake-lint=cmake_lint.__main__:main',
            'ctest-to=cmake_format.ctest_to:main'
        ],
    },
    extras_require={
        'YAML': ["pyyaml"],
        'html-gen': ["jinja2"]
    },
    install_requires=[]
)

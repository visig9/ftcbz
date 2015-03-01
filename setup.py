#!/usr/bin/env python3
# coding=utf-8

import sys

from setuptools import setup
import src.ftcbz.ftcbz

if not sys.version_info >= (3, 3, 0):
    print("ERROR: You cannot install because python version should >= 3.3")
    sys.exit(1)

setup(
    name='ftcbz',
    version=src.ftcbz.ftcbz.VERSION,
    author='Civa Lin',
    author_email='larinawf@gmail.com',
    license='MIT',
    url='https://bitbucket.org/civalin/ftcbz',
    description="A script to archive multiple comic book dir to .cbz format",
    long_description='''''',
    classifiers=[
        "Programming Language :: Python :: 3",
        "Topic :: Multimedia :: Graphics :: Graphics Conversion",
        "Topic :: System :: Archiving"],
    install_requires=[],
    setup_requires=[],
    package_dir={'': 'src'},
    packages=['ftcbz'],
    entry_points={
        'console_scripts': ['ftcbz = ftcbz.ftcbz:main'],
        'setuptools.installation': ['eggsecutable = ftcbz.ftcbz:main']
        },
    keywords='cbz comic archive',
    )

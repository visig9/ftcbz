#!/usr/bin/env python3
#-*- coding:utf-8 -*-

from setuptools import setup
# from src.ftcbz.ftcbz import program_version

setup(
    name='ftcbz',
    version='1.1.2',
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
    package_dir={'': 'src'},
    packages=['ftcbz'],
    entry_points={
        'console_scripts': ['ftcbz = ftcbz.ftcbz:main']
        },
    keywords='cbz comic',
    )

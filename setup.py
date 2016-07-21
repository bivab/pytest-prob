#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import codecs
from setuptools import setup


def read(fname):
    file_path = os.path.join(os.path.dirname(__file__), fname)
    return codecs.open(file_path, encoding='utf-8').read()


setup(
    name='pytest-prob',
    version='0.5.0-dev',
    author='David Schneider',
    author_email='david.schneider@bivab.de',
    maintainer='David Schneider',
    maintainer_email='david.schneider@bivab.de',
    license='MIT',
    url='https://github.com/bivab/pytest-prob',
    description='Pytest plugin to run B predicates as tests on ProB',
    long_description=read('README.rst'),
    py_modules=['pytest_prob'],
    install_requires=['pytest>=2.8.1', 'PyYAML>=3.11', 'pexpect>=4.0.1'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Testing',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: ISC License (ISCL)',
    ],
    entry_points={
        'pytest11': [
            'prob = pytest_prob',
        ],
    },
)

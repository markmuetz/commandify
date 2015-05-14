#!/usr/bin/env python
import os
try:
    from setuptools import setup, Extension
except ImportError:
    from distutils.core import setup, Extension

from subprocess import call

from commandify.version import get_version


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name='commandify',
    version=get_version(),
    description='Simple command line commands through decorators',
    long_description=read('README.rst'),
    author='Mark Muetzelfeldt',
    author_email='markmuetz@gmail.com',
    maintainer='Mark Muetzelfeldt',
    maintainer_email='markmuetz@gmail.com',
    packages=['commandify'],
    scripts=['commandify/commandify_examples'],
    url='https://github.com/markmuetz/commandify',
    test_suite='nose.collector',
    tests_require=['nose'],
    install_requires=[],
    data_files=[],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.7',
        ],
    keywords=['command line argument arguments'],
    )

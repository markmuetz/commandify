#!/usr/bin/env python
import os
try:
    from setuptools import setup, Extension
except ImportError:
    from distutils.core import setup, Extension


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name='commandify',
    version=read('VERSION.txt').rstrip(),
    description='Simple command line commands through decorators',
    long_description=read('README.rst'),
    author='Mark Muetzelfeldt',
    author_email='markmuetz@gmail.com',
    maintainer='Mark Muetzelfeldt',
    maintainer_email='markmuetz@gmail.com',
    packages=['commandify'],
    scripts=['commandify/commandify_examples'],
    install_requires=[],
    data_files=[],
    url='https://github.com/markmuetz/commandify',
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

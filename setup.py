#!/usr/bin/env python

import os.path, sys, os
from distutils.sysconfig import get_python_lib
try:
    from distribute import setup, find_packages
    print "Using distribute...."
except ImportError:
    from setuptools import setup, find_packages
    print "Using setuptools...."

import json
creds = json.load(open('manifest.json'))

setup(
    name=creds['name'],
    version=creds['version'],
    description=creds['description'],
    long_description=open('README.markdown').read(),
    license='MIT',
    author="Mario Fernandez",
    author_email="mario.fernandez@hceris.com",
    keywords="mailing list",
    url="https://github.com/sirech/deliver",
    download_url="https://github.com/sirech/deliver",
    packages=find_packages(exclude=[]),
    # scripts=["bin/pyblosxom-cmd"],
    # zip_safe=False,
    test_suite="deliver.tests.testrunner.test_suite",
    # include_package_data=True,
    install_requires=[
        'Mock>=0.7.0',
        ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP"
    ]
)

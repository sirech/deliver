#!/usr/bin/env python

import os.path, sys, os
from distutils.sysconfig import get_python_lib
try:
    from distribute import setup, find_packages
    print "Using distribute...."
except ImportError:
    from setuptools import setup, find_packages
    print "Using setuptools...."

version = "0.3.3"

setup(
    name="deliver",
    version=version,
    description="The astonishingly simple anonymous mailing list.",
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
    # test_suite="Pyblosxom.tests.testrunner.test_suite",
    # include_package_data=True,
    install_requires=[],
    classifiers=[
        # "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP"
    ]
)

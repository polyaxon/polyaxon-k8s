#!/usr/bin/env python

import sys

from setuptools import find_packages, setup
from setuptools.command.test import test as TestCommand


def read_readme():
    with open("README.md") as f:
        return f.read()


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest

        errcode = pytest.main(self.test_args)
        sys.exit(errcode)


setup(
    name="polyaxon-k8s",
    version="0.5.0",
    description="Polyaxon Kubernetes managers, utils, and resources.",
    long_description=read_readme(),
    maintainer="Mourad Mourafiq",
    maintainer_email="mourad@polyaxon.com",
    author="Mourad Mourafiq",
    author_email="mourad@polyaxon.com",
    url="https://github.com/polyaxon/polyaxon-k8s",
    license="MIT",
    platforms="any",
    packages=find_packages(),
    keywords=[
        "polyaxon",
        "tensorFlow",
        "deep-learning",
        "machine-learning",
        "data-science",
        "neural-networks",
        "artificial-intelligence",
        "ai",
        "reinforcement-learning",
        "kubernetes",
    ],
    install_requires=["kubernetes==10.0.1", "PyYAML>=5.1", "six>=1.12.0"],
    classifiers=[
        "Programming Language :: Python",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    tests_require=["pytest"],
    cmdclass={"test": PyTest},
)

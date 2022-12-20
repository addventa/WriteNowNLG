# -*- coding: utf-8 -*-
"""
created on 20/12/2018 16:37
@author: fgiely
"""

from setuptools import setup, find_packages
import CoreNLGMod

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="CoreNLGMod",
    version="2.1.1",
    description="",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/societe-generale/core-nlg.git",
    author="Fabien Giely",
    license="Apache v2",
    packages=find_packages(exclude=["*.logs"]),
    include_package_data=True,
    cmdclass={"package": CoreNLGMod},
    zip_safe=False,
    install_requires=["lxml"],
)

#!/usr/bin/python
#-*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        setup
# Purpose:
#
# Author:      Bclement
#
# Created:     14-03-2015
# Copyright:   (c) BClement 2015
# Licence:     GNU Affero General Public License v3.0

#-------------------------------------------------------------------------------
import re
import sys

from setuptools import setup, find_packages


def version():
    with open('experiment_manager/_version.py') as f:
        return re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", f.read()).group(1)

def requirements():
  with open('requirements.txt') as f:
    return f.readlines()

setup(name='kidlearn_lib',
      version=version(),
      author='Benjamin Clement',
      author_email='',
      url='https://github.com/flowersteam/kidlearn.git',
      description='Kidlearn library',
      install_requires=[requirements()],
      packages = find_packages(),
      license = 'GNU AFFERO GENERAL PUBLIC LICENSE Version 3',
      )
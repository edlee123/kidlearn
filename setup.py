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
from setuptools import setup, find_packages
from kidlearn_lib import __version__ as VERSION

setup(name='kidlearn_lib',
      version=VERSION,
      author='Benjamin Clement',
      author_email='',
      url='https://github.com/flowersteam/kidlearn.git',
      description='Kidelarn librairie',
      requires=['numpy','scipy','seaborn',
               ],
      packages = ['kidlearn_lib', 'kidlearn_lib.seq_manager',
                           'kidlearn_lib.experimentaion',
                           'kidlearn_lib.student',],
      )
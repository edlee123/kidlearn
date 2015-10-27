#!/usr/bin/python
#-*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        experimentation
# Purpose:
#
# Author:      Bclement
#
# Created:     14-03-2015
# Copyright:   (c) BClement 2015
# Licence:     GNU Affero General Public License v3.0
#-------------------------------------------------------------------------------

import functions as func
import numpy as np
import copy as copy
import json
import os
import re

def perturb_KT_model(perturbation, stud_params = None, params_file = None, directory = None):
    stud_params = stud_params or func.load_json(params_file,directory)

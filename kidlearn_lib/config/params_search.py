#-*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        params_search
# Purpose:
#
# Author:      Bclement
#
# Created:     04-09-2015
# Copyright:   (c) BClement 2015
# Licence:     GNU Affero General Public License v3.0
#-------------------------------------------------------------------------------

import functions as func
import numpy as np
import copy as copy
import json
import os
import config
from scipy.optimize import curve_fit

def greed_search():
    return
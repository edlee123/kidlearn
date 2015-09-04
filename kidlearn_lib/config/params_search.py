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

def func(x, a, b, c):
    return a * np.exp(b * x) + c

xdata = np.linspace(0, 4, 50)
y = func(xdata, 2.5, 1.3, 0.5)
ydata = y + 0.2 * np.random.normal(size=len(xdata))

popt, pcov = curve_fit(func, xdata, ydata)
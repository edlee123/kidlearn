#-*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        circospy
# Purpose:
#
# Author:      Bclement
#
# Created:     14-03-2015
# Copyright:   (c) BClement 2015
# Licence:     GNU GENERAL PUBLIC LICENSE

#-------------------------------------------------------------------------------

import sys as sys
import numpy as np
import scipy as scipy
import scipy.stats as sstats
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.patches import Rectangle
import pylab as pylab
from my_functions import *

from scipy.cluster.vq import vq, kmeans, whiten, kmeans2
import copy

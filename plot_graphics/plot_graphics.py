#-*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        graph_lib
# Purpose:
#
# Author:      Bclement
#
# Created:     14-03-2015
# Copyright:   (c) BClement 2015
# Licence:     GNU Affero General Public License v3.0

#-------------------------------------------------------------------------------
from custom_graph import *
import sys as sys
import numpy as np
import scipy as scipy
import scipy.stats as sstats
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.patches import Rectangle
import pylab as pylab

from scipy.cluster.vq import vq, kmeans, whiten, kmeans2
import copy

import kidlearnGraph as kGraph

def draw_logistic(alpha = [-20],beta  = [0.1], linspace = [-1,1]):
    #x = np.linspace(-1, 1)
    x = np.linspace(*linspace)
    for a,b in zip(alpha,beta):
        plt.plot(x,1.0/(1+1*np.exp(-a*(x-b))))
    #plt.plot(x, (1.0/pi)*arctan((x+ 0.08)*15) + 0.5)
    #plt.plot(x, (1.0/pi)*arctan((x+ 0.06)*20) + 0.5)
    #plt.plot(x, (1.0/pi)*arctan((x+ 0.04)*30) + 0.5)
    #plt.plot(x, (1.0/pi)*arctan((x +0.02)*60) + 0.5)
    #plt.plot(x, (1.0/pi)*arctan((x +0.1)*100) + 0.5)
    #plt.plot(x, (a/pi)*arctan((x + b)*c) + d)
    #plt.plot(x,1.0/(1+1*exp(-10*(x-0.1))))
    #plt.plot(x,0.6*(1+x*8))
    #plt.plot(x,1.0/(1+1*exp(-20*(x-0.07))))
    #plt.plot(x,1.0/(1+1*exp(-40*(x+0.07))))
    #plt.plot(x, ((1.0/pi)*arctan((x - 0.1)*30) + 0.5)*1)
    #plt.plot(x, 1 - ((1.0/pi)*arctan((x - 0.25)*17) + 0.5)*1)
    plt.axis('tight')
    plt.show()

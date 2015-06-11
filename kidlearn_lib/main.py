#-*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        sim_launcher
# Purpose:
#
# Author:      Bclement
#
# Created:     14-03-2015
# Copyright:   (c) BClement 2015
# Licence:     GNU GENERAL PUBLIC LICENSE

#-------------------------------------------------------------------------------

import numpy as np
import copy as copy
import json
import config
import os

from simulation import *



#graph.kGraph.plot_cluster_lvl_sub([data],100,100, title = "%s \nStudent distribution per erxercices type over time" % ("test"),path = "graphics/", ref = "clust_xseq_global_%s" % ("test"),legend = ["M1","M2","M3","M4","M5","M6","R1","R2","R3","R4","MM1","MM2","MM3","MM4","RM1","RM2","RM3","RM4"],dataToUse = range(len([data])))
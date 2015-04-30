#-*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        config
# Purpose:
#
# Author:      Bclement
#
# Created:     14-03-2015
# Copyright:   (c) BClement 2015
# Licence:     GNU GENERAL PUBLIC LICENSE
#-------------------------------------------------------------------------------

from seq_manager import * #Sequence, ZPDES_hssbg, RIARIT_hssbg, Random_sequence
from exercise import Exercise
from student import *
from knowledge import *
import numpy as np
import copy as copy
import json
import os

class Config(object):
    def __init__(self):
        knowledges_conf = []
        knowledges_conf.append({"name" : "S1", "num_id":0, "beta_0": 0.1, "beta":[0.2,0,0]})
        knowledges_conf.append({"name" : "S2", "num_id":1, "beta_0": 0, "beta":[0,0.2,0]})
        knowledges_conf.append({"name" : "S3", "num_id":2, "beta_0": 0, "beta":[0.3,0,0.1]})
        self._knowledges_conf = knowledges_conf

        exercises = []
        exercises.append(Exercise(0,gamma = [1,0,0]))
        exercises.append(Exercise(0,gamma = [0.7,0,0]))
        exercises.append(Exercise(0,gamma = [0,0.7,0]))
        exercises.append(Exercise(0,gamma = [0.1,0,0.8]))
        exercises.append(Exercise(0,gamma = [0.3,0,0.6]))
        exercises.append(Exercise(0,gamma = [0.3,0.3,0.3]))
        self._exercises = exercises

    """
    TO DO : 
    Load config file
    Load json file
    Load with direct parameter
    Load config from an other simulation (config copy)
    """
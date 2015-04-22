#-*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        knowledge
# Purpose:
#
# Author:      Bclement
#
# Created:     14-03-2015
# Copyright:   (c) BClement 2015
# Licence:     CreativeCommon
#-------------------------------------------------------------------------------

import os
from numpy import *
import re
import pickle
import json
from functions import *

class Knowledge(object):
    def __init__(self,name, level = 0, num_id = 0, *args, **kwargs):
        self._id = num_id
        self._name = name
        self._level = level

        for key, val in kwargs.iteritems():
            object.__setattr__(self, key, val)

    def __repr__(self):
        return "%s : %s" % (self._name,self._level)
    
    def __str__(self):
        return self.__repr__()
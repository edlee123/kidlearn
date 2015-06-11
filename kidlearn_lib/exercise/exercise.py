#-*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        exercise
# Purpose:
#
# Author:      Bclement
#
# Created:     14-03-2015
# Copyright:   (c) BClement 2015
# Licence:     GNU GENERAL PUBLIC LICENSE

#-------------------------------------------------------------------------------

import numpy as np
import copy
import re
from knowledge import *

class Exercise(object):

    def __init__(self,ex_params,knowledge_levels = None, knowledge_names = None, answer = None, gamma = [], params = {}, *args,**kwargs):
        # ex_params : 

        self._gamma = np.array(gamma)
        self._ex_params = ex_params
        self._answer = answer
        self._knowledges = [Knowledge(kn,kl) for (kn,kl) in zip(knowledge_names,knowledge_levels)]
        self.add_attr(args,kwargs)

    @property
    def ex_params(self):
        return self._ex_params

    @property
    def gamma(self):
        return self._gamma
    
    @property
    def answer(self):
        return self._answer

    @property
    def knowledges(self):
        return self._knowledges

    def __repr__(self):
        #print "act : %s" % self._ex_params
        #print "ans : %s" % self._answer
        act = copy.deepcopy(self._ex_params)
        act["CS"] = self._answer
        return act.__str__()
    
    def __str__(self):
        return self.__repr__()

    def get_knowledges_worked(self, by_names = 0, by_gamma = 1):
        if by_gamma:
            return [int(gamma > 0) for gamma in self._gamma]
        elif by_names:
            return [kc._name for kc in self._knowledges if kc._level != 0]
        else:
            return [self._knowledges.index(kc) for kc in self._knowledges if kc._level != 0]

    def get_knowledges_level(self):
        levels = []
        for kc in self._knowledges:
            levels.append(kc._level)
        return levels

    def get_attr(self):
        return {"ex_params": self._ex_params, "knowledge" : self._knowledges, "answer" : self._answer}

    def add_attr(self,*args,**kwargs):
        for key, val in kwargs.iteritems():
            object.__setattr__(self, key, val)

#-*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        exercise
# Purpose:
#
# Author:      Bclement
#
# Created:     14-03-2015
# Copyright:   (c) BClement 2015
# Licence:     GNU Affero General Public License v3.0

#-------------------------------------------------------------------------------

import numpy as np
import copy
import re

from ..knowledge import Knowledge

class Exercise(object):

    def __init__(self, act, knowledge_levels=None, knowledge_names=None, 
            answer=None, nbMax_try=1, params=None, *args,**kwargs):
        # act : 

        self._act = act
        self._answer = answer
        self._knowledges = [Knowledge(kn,kl) for (kn,kl) in zip(knowledge_names,knowledge_levels)]
        
        self._nbMax_try = nbMax_try
        params = np.array(params)
        
        self.add_attr(args,kwargs)

    @property
    def state(self):
        state = {}
        state["act"] = self._act
        state["answer"] = self._answer
        state["knowledges"] = self.get_knowledges_level()
        return state

    @property
    def nbMax_try(self):
        return self._nbMax_try

    @property
    def act(self):
        return self._act
    
    @property
    def answer(self):
        return self._answer

    @property
    def knowledges(self):
        return self._knowledges

    def __repr__(self):
        #print "act : %s" % self._act
        #print "ans : %s" % self._answer
        act = copy.deepcopy(self._act)
        act["ans"] = self._answer
        return act.__str__()
    
    def __str__(self):
        return self.__repr__()

    def get_knowledges_worked(self, by_names=0, by_gamma=1):
        if by_gamma:
            return [int(gamma > 0) for gamma in self._gamma]
        elif by_names:
            return [kc._name for kc in self._knowledges if kc._level != 0]
        else:
            return [self._knowledges.index(kc) for kc in self._knowledges if kc._level != 0]

    def get_knowledges_level(self):
        return np.array([kc._level for kc in self._knowledges])

    def get_attr(self):
        return {"act": self._act, "knowledge" : self._knowledges, "answer" : self._answer}

    def add_attr(self, *args, **kwargs):
        for key, val in kwargs.iteritems():
            object.__setattr__(self, key, val)

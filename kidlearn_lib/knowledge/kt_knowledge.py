#-*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        kt_knowledge
#Purpose:
#
# Author:      Bclement
#
# Created:     14-03-2015
# Copyright:   (c) BClement 2015
# Licence:     CreativeCommon
#-------------------------------------------------------------------------------

from numpy import *
import copy
import re
import json
from operator import mul
from knowledge import *

################################################################################
################################################################################
## Class KT Knowledge basic

class KT_knowledge(Knowledge):
    def __init__(self,name, KT_params = None, level = 0, num_id = None):
        Knowledge.__init__(self,name,level,num_id)
        KT_params = KT_params or {"L0" : 0.02,"T": 0.01, "G" : 0.1, "S" : 0.1}
        self._p_Lt = [KT_params["L0"]]
        self._p_T = KT_params["T"]
        self._p_G = KT_params["G"]
        self._p_S = KT_params["S"]
        self._p_correct = self._p_G
        self.update_knowledge(self._p_Lt[0])

    def __repr__(self):
        return "%s : %s" % (self._name,self._p_Lt[-1])
    
    def __str__(self):
        return self.__repr__()

    # knowledge = 0 or 1 , updated at each step
    ###################################################
    def update_knowledge(self,prob = None):
        prob = prob or self._p_T
        if self._level != 1:
            learn = random.multinomial(1,[1-prob,prob])
            self._level = nonzero(learn==1)[0][0]
            
    ###################################################
    def transition_prob(self):
        return self._p_T

    def emission_prob(self):
        if self._level == 1:
                #print self._name + "learned"
            self._p_correct = 1 - self._p_S

    # Predict performance
    def compute_performance_prediction(self):
        p_correct = self._p_Lt[-1]*(1-self._p_S) + (1-self._p_Lt[-1])*self._p_G
        print "p_correct : %s" % p_correct
        return p_correct

    # Compute proba of master the skill
    def update_predict_mastered(self,obs):
        p_Lt = self.compute_p_Lt_koedinger(obs)
        self._p_Lt.append(p_Lt)
        print "p_lt_koed : %s" % p_Lt

    def compute_p_Lt_koedinger(self,obs):
        p_Lt_obs = self.calcul_p_Lt_obs(obs,self._p_Lt[-1])
        p_Lt_obs = p_Lt_obs + (1 - p_Lt_obs)*self._p_T
        return p_Lt_obs

    def compute_p_Lt_edm(self,obs):
        num = (1-self._p_T)*(1-self._p_Lt_edm[-1])*(1 - obs + pow(-1,1-obs)*self._p_G)
        denum = 1 - obs + pow(-1,1-obs)*self._p_G + pow(-1,1-obs)*(1 - self._p_S-self._p_G)*self._p_Lt_edm[-1]
        p_Lt_obs = 1 - num/denum
        return p_Lt_obs

    def calcul_p_Lt_obs(self,obs,p_Lt):
        slip_factor = (obs + pow(-1,obs)*self._p_S)*p_Lt
        guess_factor = (1 - p_Lt) * (1 - obs + pow(-1,1-obs)*self._p_G)
        p_Lt_obs = slip_factor / (slip_factor + guess_factor)
        return p_Lt_obs


    ######## ERROR PAPER ###############################################
    def compute_p_Lt_burnskill(self,obs):
        p_Lt = self._p_Lt[-1] + self._p_T*(1-self._p_Lt[-1])
        p_Lt_obs = self.calcul_p_Lt_obs(obs,p_Lt)
        return p_Lt_obs

## Class KT Knowledge basic
################################################################################
################################################################################

#-*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        kt_knowledge
#Purpose:
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
import json
from operator import mul
from knowledge import *

################################################################################
################################################################################
## Class KT Knowledge basic

class KTKnowledge(Knowledge):
    def __init__(self, name = None,level = None, params = None):# KT_params = None, level = 0, num_id = None):
        Knowledge.__init__(self,name,level)
        self.params = params
        self.p_L0 = self.params["L0"]
        self.p_T = self.params["T"]

        if not isinstance(self.p_T,list):
            self.p_T = [self.p_T]
        
        #self.kc_trans_dep = self.params["kc_trans_dep"]

        self.p_G = self.params["G"]
        self.p_S = self.params["S"]
        self.update_state(self.p_L0)
        if self._level == 1 :
            print self.p_L0
            raw_input()

    # knowledge = 0 or 1 , updated at each step
    ###################################################
    def update_state(self,prob = None, adding_prob = 0, pT_idx = 0):
        if prob != None:
            prob = prob
        else:
            prob = adding_prob + self.p_T[pT_idx]

        if self._level != 1:
            learn = np.random.multinomial(1,[1-prob,prob])
            learn = np.nonzero(learn==1)[0][0]
            if learn : 
                self._level = 1
            
    ###################################################
    def transition_prob(self,pT_idx = 0):
        return self.p_T[pT_idx]

    def emission_prob(self):
        if self._level == 1:
            #print self._name + "learned"
            return 1 - self.p_S
        else:
            return self.p_G


## Class KT Knowledge basic
################################################################################
################################################################################

################################################################################
################################################################################
## Class KT Knowledge Predictor

class KTPredictPerf(object):

    def init(self,kt_knowledge):
        self.ktComp = kt_knowledge
        self.p_Lt = [self.ktComp.p_l0]
    # Predict performance
    def compute_performance_prediction(self):
        p_correct = self.p_Lt[-1]*(1-self._p_S) + (1-self.p_Lt[-1])*self._p_G
        print "p_correct : %s" % p_correct
        return p_correct

    # Compute proba of master the skill
    def update_predict_mastered(self,obs):
        p_Lt = self.computep_Lt_koedinger(obs)
        self.p_Lt.append(p_Lt)
        print "p_lt_koed : %s" % p_Lt

    def computep_Lt_koedinger(self,obs,pT_idx = 0):
        p_Lt_obs = self.calculp_Lt_obs(obs,self.p_Lt[-1])
        p_Lt_obs = p_Lt_obs + (1 - p_Lt_obs)*self.ktComp.p_T[pT_idx]
        return p_Lt_obs

    def computep_Lt_edm(self,obs):
        num = (1-self.ktComp.p_T[pT_idx])*(1-self.p_Lt_edm[-1])*(1 - obs + pow(-1,1-obs)*self._p_G)
        denum = 1 - obs + pow(-1,1-obs)*self._p_G + pow(-1,1-obs)*(1 - self._p_S-self._p_G)*self.p_Lt_edm[-1]
        p_Lt_obs = 1 - num/denum
        return p_Lt_obs

    def calculp_Lt_obs(self,obs,p_Lt):
        slip_factor = (obs + pow(-1,obs)*self._p_S)*p_Lt
        guess_factor = (1 - p_Lt) * (1 - obs + pow(-1,1-obs)*self._p_G)
        p_Lt_obs = slip_factor / (slip_factor + guess_factor)
        return p_Lt_obs


## Class KT Knowledge Predictor
################################################################################
################################################################################
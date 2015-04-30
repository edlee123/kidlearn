#-*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        kt_features
#Purpose:
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
import json
from operator import mul
from kt_knowledge import *
import math


################################################################################
################################################################################
## Class KT Knowledge feature

class KT_features(KT_knowledge):
    def __init__(self,name, num_id, beta_0 = None, beta = None,level = 0, *args,**kwargs):# knowledge_params = {},
    #,subs_names = None, subs_levels = None, subs_trans_param = None, subs_emission_param= None):
        Knowledge.__init__(self,name,level,num_id,**kwargs)
        self._beta_0 = beta_0 #or knowledge_params["beta_0"]
        self._beta = np.array(beta)# or knowledge_params["beta"])

        self._p_Lt = []
        #self._subskills = subskills or []
        #if subskills != None or subs_trans_param != None:
        #    self._subskills = subskills or [KT_features(sn,sl,beta = stp) for (sn,sl,stp) in zip(subs_names,subs_levels,subs_trans_param)]
        #    self.transition_prob([subs._name for subs in self._subskills],step = 0)
        self.update_knowledge(prob = self._beta_0)

    def __repr__(self):
        return "%s : %s" % (self._name,self._level)
    
    def __str__(self):
        return self.__repr__()

    #def get_subskill(self,index = 0, name = None):
    #    if name != None:
    #        for subskill in self._subskills:
    #            if subskill._name == name:
    #                return subskill
    #    return self._subskills[index]

    #def get_subskill_level(self): 
    #    return [subskill._level for subskill in self._subskills]

    def update_knowledge(self,exercise = None,stud_knowledge = None,prob = None):
        if prob != None:
            self._p_T = prob 
        else: 
            self._p_T = self.transition_prob(exercise,stud_knowledge)
        KT_knowledge.update_knowledge(self)

    def transition_prob(self,exercise,stud_knowledge = None):
        subskill_mastery = stud_knowledge #or np.array([subskill._level for subskill in self._subskills])
        exercise_skills = np.array(exercise.get_knowledges_worked(by_gamma = 1))
        subskill_factor = sum(self._beta*exercise_skills* subskill_mastery)
        self._p_T = exercise_skills[self._id]*logistic_function(self._beta[self._id] + subskill_factor)
        print "ex_skill %s, subs_factor : %s, self_beta : %s" % (exercise_skills,subskill_factor,self._beta[self._id])
        return self._p_T

    def emission_prob(self,exercise):
        return


## Class KT Knowledge feature
################################################################################
################################################################################
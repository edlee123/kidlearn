#-*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        kt_student
#Purpose:
#
# Author:      Bclement
#
# Created:     14-03-2015
# Copyright:   (c) BClement 2015
# Licence:     CreativeCommon
#-------------------------------------------------------------------------------

import numpy as np
import copy
import re
import json
from operator import mul
from student import *


################################################################################
## Class KT student
################################################################################

class KT_student(Student):
    def __init__(self,kc_params,id = "x"):
        Student.__init__(self,id)
        for i in range(len(kc_params)):
            self._knowledges.append(KT_features(**kc_params[i]))

    def __repr__(self):
        str = ""
        for kc in self._knowledges:
            str += kc.__repr__() + ", "
        return str
    
    def __str__(self):
        return self.__repr__()

    def get_state(self, seq_values = None):
        student_state = Student.get_state(self)
        student_state["knowledges"] = self._knowledges
        return student_state

    def update_mastery(self,exercise):
        for kc in self._knowledges:
            kc.update_knowledge(exercise,self.get_kc_mastery())
            print "%s T : %s Lvl : %s " % (kc._name, kc._p_T, kc._level)

    def get_kc_mastery(self):
        return np.array([kc._level for kc in self._knowledges])

    def emission_prob(self,exercise):
        emmission_factor = sum(self.get_kc_mastery()*exercise._gamma)
        return logistic_function(emmission_factor)
        

    def answer(self,exercise):
        #Emission probablity
        p_correct = self.emission_prob(exercise)
        print "p_correct : %s " % p_correct
        # Answer / Observation
        s = random.multinomial(1,[1-p_correct,p_correct])
        ans = nonzero(s==1)[0][0]
                
        # Transition computation
        self.update_mastery(exercise)
        
        exercise._answer = ans
        exercise.add_attr(_nb_try = 1)
        return exercise

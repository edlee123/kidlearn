#-*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        KTStudent
#Purpose:
#
# Author:      Bclement
#
# Created:     14-03-2015
# Copyright:   (c) BClement 2015
# Licence:     GNU Affero General Public License v3.0

#-------------------------------------------------------------------------------

from operator import mul
from student import *
import function as func
import knowledge as knl
import numpy as np
import scipy.stats as sstats


################################################################################
## Class KT student
################################################################################

class KTStudent(Student)
    def __init__(self,params = None, params_file = "qstud_test_1", directory = "params_files", *args, **kwargs):
        self.params = params or func.load_json(params_file,directory)

        Student.__init__(self,id)
        for i in range(self.params["knowledges_names"]):
            name = self.params["knowledges_names"][i]
            level = self.params["knowledge_levels"][i]
            params = {}
            for kt_keys in self.params["KT"].keys():
                params[kt_keys] = self.params["KT"][kt_keys][i]
            
            self._knowledges.append(knl.KTKnowledge(name,level, params))

    def __repr__(self):
        str = ""
        for kc in self._knowledges:
            str += kc.__repr__() + ", "
        return str

    def get_knowledge(self,name, *arg, **kwargs):
        idx = self.params["knowledge_names"].index(name)
        return self._knowledge[idx]

    def update_mastery(self,exercise):
        for kc in exercise._knowledges:
            self.get_knowledge(kc.name).update_state()

    def get_kc_mastery(self):
        return np.array([kc._level for kc in self._knowledges])

    def emission_prob(self,exercise):
        prob_correct = []
        for kc in exercise._knowledges:
            prob_correct.append(self.get_knowledge(kc.name).emission_prob())

        return np.mean(prob_correct)
        

    def answer(self,exercise):
        #Emission probablity
        p_correct = self.emission_prob(exercise)
        print "p_correct : %s " % p_correct
        # Answer / Observation
        s = np.random.multinomial(1,[1-p_correct,p_correct])
        ans = np.nonzero(s==1)[0][0]
                
        # Transition computation
        self.update_mastery(exercise)
        
        exercise._answer = ans
        exercise.add_attr(_nb_try = 1)
        return exercise

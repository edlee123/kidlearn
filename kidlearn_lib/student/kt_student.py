#-*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        KTstudent
#Purpose:
#
# Author:      Bclement
#
# Created:     14-03-2015
# Copyright:   (c) BClement 2015
# Licence:     GNU Affero General Public License v3.0

#-------------------------------------------------------------------------------
import numpy as np
import scipy.stats as sstats
from operator import mul

from .student import Student
from ..knowledge import Knowledge, KTKnowledge
from .. import functions as func


################################################################################
## Class KT student
################################################################################

class KTstudent(Student):

    def __init__(self,params = None, params_file = "kt_stud", directory = "params_files", *args, **kwargs):
        params = params or func.load_json(params_file,directory)
        
        Student.__init__(self, params = params)
        
        for i in range(len(self.params["knowledge_names"])):
            name = self.params["knowledge_names"][i]
            level = self.params["knowledge_levels"][i]
            kc_params = {}
            for kt_keys in self.params["KT"].keys():
                kc_params[kt_keys] = self.params["KT"][kt_keys][i]
            
            self._knowledges.append(KTKnowledge(name,level,kc_params))

        self.kc_trans_dep = np.array(self.params["kc_trans_dep"])

    def __repr__(self):
        str = ""
        for kc in self._knowledges:
            str += kc.__repr__() + ", "
        return str

    @property
    def KC_names(self):
        return self.params["knowledge_names"] 

    def get_knowledge_idx(self,name, *arg, **kwargs):
        return self.params["knowledge_names"].index(name)

    def get_knowledge(self,name, *arg, **kwargs):
        idx = self.get_knowledge_idx(name)
        return self._knowledges[idx]

    def learn(self,exercise):
        for kc in exercise._knowledges:
            if kc.level > 0 :
                kc_levels = np.array(self.get_kc_lvl())
                depend_val = self.kc_trans_dep[self.get_knowledge_idx(kc.name),:]
                depend_prob = np.dot(kc_levels,depend_val) 
                self.get_knowledge(kc.name).update_state(adding_prob = depend_prob)

    def emission_prob(self,exercise):
        prob_correct = []
        for kc in exercise._knowledges:
            if kc.level > 0 :
                prob_correct.append(self.get_knowledge(kc.name).emission_prob())

        return np.mean(prob_correct)

    def answer(self,exercise, nb_try = 1):
        
        # Transition computation
        self.learn(exercise)
        
        #Emission probablity
        p_correct = self.emission_prob(exercise)

        # Answer / Observation
        s = np.random.multinomial(1,[1-p_correct,p_correct])
        ans = np.nonzero(s==1)[0][0]
                
        exercise._answer = ans
        exercise.add_attr(_nb_try = 1)
        return exercise

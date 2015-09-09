#-*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        student
# Purpose:
#
# Author:      Bclement
#
# Created:     14-03-2015
# Copyright:   (c) BClement 2015
# Licence:     GNU Affero General Public License v3.0
#-------------------------------------------------------------------------------
#from ..functions, knowledge 
#from ..knowledge import knowledge as knl
import knowledge as knl
import functions as func
import numpy as np
import os
import re
import pickle
import json
import copy

class Student(object):

    def __init__(self,id = "x", params = None):
        self.params = params
        if "id" in params.keys():
            self._id = params["id"]
        else:
            self._id = id
        self._knowledges = []
        self.logs = {}
        #self._skills = skills
        return

    @property
    def id(self):
        return self._id
    

    def get_state(self, seq_values = None):
        student_state = {}
        student_state["id"] = self._id
        student_state["knowledges"] = self._knowledges

        return student_state

    def answer(self,exercise = None, ans = None, nb_try = 0):
        exercise._answer = ans
        exercise.add_attr(_nb_try = nb_try)
        return exercise

    def try_and_answer(self,prob_correct = 0, exercise = None):
        nb_try = 0
        ans = 0
        while ans == 0 and nb_try < exercise.nbMax_try:
            s = np.random.multinomial(1,[1-prob_correct,prob_correct])
            ans = np.nonzero(s==1)[0][0]
            if ans == 0:
                nb_try += 1

        #self.motivation = min(max(self.motivation + (ans-0.5)/50,0.5),2)
        exercise._answer = ans
        exercise.add_attr(_nb_try = nb_try)
        return exercise


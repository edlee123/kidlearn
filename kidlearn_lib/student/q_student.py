#-*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        q_student
#Purpose:
#
# Author:      Bclement
#
# Created:     14-03-2015
# Copyright:   (c) BClement 2015
# Licence:     GNU Affero General Public License v3.0

#-------------------------------------------------------------------------------
import numpy as np

from .student import Student
from ..functions import functions as func
from ..knowledge import Knowledge

class Qstudent(Student):

    def __init__(self, params = None, params_file = "qstud_test_1", directory = "params_files", *args, **kwargs):
        params = params or func.load_json(params_file,directory)

        Student.__init__(self, params = params)

        self._knowledges = [Knowledge(kn,kl) for (kn,kl) in zip(self.params["knowledge_names"],self.params["knowledge_levels"])]
        
        if "logistic_values" in self.params.keys():
            self.log_vals = self.params["logistic_values"]
        else:
            self.log_vals = {"learn" : [-20,0.07], "ans" : [-20,0.1]}

        self.guess_prob = 1 #0.7  #0.7
        self.min_prob = 0
        self.threshold_prob = 0
        self.learning_progress = [1,1,1,1,1,1,1] # [0.5,0.5,0.5,0.5,0.5,0.5] # [0.2,0.2,0.2,0.2,0.2,0.2] 
        #self.nbTry = nb_try # ssb_data["nb_try"]

        #Not use now
        #self.motivation = 1
        #self.lvl_up_prob = 0.8 #0.6
        #student_state["skills"] = self._skills

    @property
    def knowledges(self):
        return self._knowledges
    

    def get_state(self, seq_values = None):
        student_state = Student.get_state(self)

        return student_state


    def calcul_prob_learn(self,lvls_ex,prob = 1):
        probas = []
        #distTot = [self._knowledges[i]._level - lvls_ex[i] for i in range(len(lvls_ex))]
        #distTot = sum(distTot)/len(lvls_ex)
        #coeffDist = 1 - min(max(0,distTot),1)

        for i in range(len(lvls_ex)):
            #p = self.lvl_up_prob*(1-(lvls_ex[i] - self._knowledges[i]._level)*self.coeff_lvl_up)
            if lvls_ex[i] - self._knowledges[i]._level  > 0.4:
                p = 0
            else:
                p = (1.0/(1+1*np.exp(self.log_vals["learn"][0]*(self._knowledges[i]._level - lvls_ex[i]+self.log_vals["learn"][1]))))
            
            p  = p * prob
            p = min(1,max(self.min_prob,p))
            probas.append(p)

        return probas

    def learn(self,lvls_ex,prob = 1):
        prob_learn_tab = self.calcul_prob_learn(lvls_ex,prob)
        for i in range(0,len(lvls_ex)):
            s = np.random.multinomial(1,[1-prob_learn_tab[i],prob_learn_tab[i]]) 
            lvl_up = np.nonzero(s==1)[0][0]
            if lvl_up and self._knowledges[i]._level < lvls_ex[i]:
                coef_up = max(0.00,self.learning_progress[i] * (lvls_ex[i]-self._knowledges[i]._level))
                newlvl = min(self._knowledges[i]._level + coef_up,lvls_ex[i])
                if i > 3:
                    if newlvl <= self._knowledges[i-3]:
                        self._knowledges[i]._level = newlvl
                else:
                    self._knowledges[i]._level = newlvl
        return

    def calcul_prob_answer_per_skill(self,lvls_ex):
        probas = []
        for i in range(0,len(lvls_ex)):
            if lvls_ex[i] - self._knowledges[i]._level  > 0.6:
                p = 0
            else:
            #p = self.guess_prob*((1.0/pi)*arctan((self._knowledges[i]._level - lvls_ex[i] + 0.1)*30) + 0.5)
                p = self.guess_prob*(1.0/(1+1*np.exp(self.log_vals["ans"][0]*(self._knowledges[i]._level - lvls_ex[i]+self.log_vals["learn"][1]))))
            probas.append(p)

        return probas

    def compute_prob_correct_answer(self,lvls):
        nb_skills = len(lvls)
        prob_tab = self.calcul_prob_answer_per_skill(lvls)
        #weight = [1,1,1,1,1,1]
        prob = 1
        for x in prob_tab:
            prob = prob*x
        prob = pow(prob,1.0/nb_skills)
        
        if prob < self.threshold_prob :
            prob = 0
        
        return prob

    def answer(self,exercise, nb_try = 0):#act,lvls):
        self.learn(exercise.get_knowledges_level())
        prob_correct = self.compute_prob_correct_answer(exercise.get_knowledges_level())
        #print prob_correct
        #s = np.random.multinomial(1,[1-prob_correct,prob_correct]) 
        #cor = np.nonzero(s==1)[0][0]
        return self.try_and_answer(prob_correct,exercise)



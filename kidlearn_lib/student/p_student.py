#-*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        p_student
# Purpose:
#
# Author:      Bclement
#
# Created:     14-03-2015
# Copyright:   (c) BClement 2015
# Licence:     GNU Affero General Public License v3.0
#-------------------------------------------------------------------------------
import numpy as np

from .q_student import Qstudent
from .. import functions as func

class Pstudent(Qstudent):

    def __init__(self,id = "x", params = {}, knowledge_levels = [0.3,0.3,0.2,0.1,0.1,0.1,0.1], knowledge_names = ["KnowMoney","IntSum","IntSub","IntDec","DecSum","DecSub","DecDec"], p_learn_prog = [0.001,0.001,0.001,0.001], threshold = 0, nb_try = 3):
        #print skills
        Qstudent.__init__(self,knowledge_level,knowledge_names, threshold = threshold, nb_try = nb_try)
        #print "p_s : %s" % threshold
        #param : lvl,JustSound,TypePrice,NotTok,ShowSum
        self.p_lvl = {}
        tab = self.tab_param()
        for key,param in params.items():
            self.p_lvl[key] = []
            for i in range(0,len(param)):
                #print self.choose_tab(tab[key][i],param[i])
                self.p_lvl[key].append(self.choose_tab(tab[key][i],param[i]))

        self.p_learning = p_learn_prog
        self.p_lvl_up_prob = 1 #0.6
        

    def get_state(self, seq_values = None):
        student_state = Qstudent.get_state(self)
        student_state["p_lvl"] = self.p_lvl

        return student_state

    def learn(self,act,lvls_ex):
        
        prob_tab = self.calcul_prob_learn(lvls_ex)
        prob = 1

        for x in prob_tab:
            prob = prob*x
        prob = pow(prob,1.0/len(prob_tab))
        prob = prob*self.p_lvl_up_prob

        for key,actspe in act.items():
            for i in range(len(actspe)):
                s = np.random.multinomial(1,[1-prob,prob]) 
                do_lvl_up = np.nonzero(s==1)[0][0]
                if do_lvl_up :
                    lvl_up = self.p_learning[i] * (1-self.p_lvl[key][i][actspe[i]])  
                    self.p_lvl[key][i][actspe[i]] = min(self.p_lvl[key][i][actspe[i]] + lvl_up,1)
                
        return

    def compute_prob_correct_answer(self,act):

        nb_param = len(act)
        prob_tab = []

        #print self.p_lvl
        for key,actspe in act.items():
            for i in range(0,len(actspe)) :
                prob_tab.append(self.p_lvl[key][i][actspe[i]])
        #weight = [1,1,1,1]
        prob = 1
        #print prob_tab
        for x in prob_tab:
            prob = prob*x

        prob = pow(prob,1.0/nb_param)
        return prob


    def answer(self,exercise, answer = None, nb_try = 0):#act,lvls):

        self.learn(exercise._params,exercise._skills)
        Qstudent.learn(self,exercise._skills,prob)
        prob_correct = self.compute_prob_correct_answer(act)*Qstudent.compute_prob_correct_answer(self,exercise._skills)
        prob_correct = pow(prob_correct,1)
        
        return self.try_and_answer(prob_correct,exercise)

    def choose_tab(self,_tab,_type):
        if _type < len(_tab) :
            choosing_tab = _tab[_type]
        else :
            choosing_tab = _tab[0]
        
        return choosing_tab


    # Add you configuration of parameters
    def tab_param(self):

            """
            Todo : Nouvelle prise en compte des parametres, chaque table donnera lieu a une liste de niveau par exemple :
            tab_val["mod"] =   [[[1,1,1],
                                [0,1,0],
                                [1,1,0]],
                                [[1,1],
                                [],
                                []],
                                [[],
                                [],
                                []],
                                [[],
                                [],
                                []]]
            """
            tabParam = {}

            tabParam["MAIN"] = [[[1, 1, 1, 1],              # 0
                       [1, 1, 0.1, 0.1],              # 1
                       [1, 0.7, 0.4, 0.1],      # 2
                       [1, 0.8, 0.6, 0.4],      # 3
                       [1, 1, 1, 0.8],        # 4
                       [0.9, 0.9, 0.9, 0.8],  # 5
                       [0.7, 0.5, 0.5, 0.2],    # 6
                       [0.8, 0.6, 0.4, 0.2],      # 7
                       [0.9, 0.8, 0.7, 0.6],  # 8
                       [0.5, 0.4, 0.4, 0.3]]]  # 9
            
            tabParam["M"] = [[[1, 1, 1, 1, 1, 1],       # 0
                       [1, 1, 1, 0.1, 0.1, 0.1],              # 1
                       [1, 1, 1, 0.5, 0.5, 0.5],      # 2
                       [1, 0.8, 0.8, 0.4, 0.4, 0],      # 3
                       [1, 1, 1, 0.8, 0.8, 0.5],        # 4
                       [0.9, 0.9, 0.9, 0.8, 0.8, 0.7],  # 5
                       [0.7, 0.5, 0.5, 0.2, 0.2, 0],    # 6
                       [0.8, 0.6, 0.4, 0.2, 0, 0],      # 7
                       [0.9, 0.8, 0.7, 0.6, 0.5, 0.4],  # 8
                       [1, 0, 1, 0, 1, 0],              # 9
                       [0, 1, 0, 1, 0, 1],              # 10
                       [0.4, 0.5, 0.6, 1, 1, 1],        # 11
                       [0.5, 0.4, 0.4, 0.3, 0.3, 0.3]]]  # 12

            tabParam["R"] = [[[1, 1, 1, 1],              # 0
                       [1, 1, 0.1, 0.1],              # 1
                       [1, 1, 0.1, 0.1],      # 2
                       [1, 0.8, 0.8, 0.4],      # 3
                       [1, 1, 1, 0.8],        # 4
                       [0.9, 0.9, 0.9, 0.8],  # 5
                       [0.7, 0.5, 0.5, 0.2],    # 6
                       [0.8, 0.6, 0.4, 0.2],      # 7
                       [0.9, 0.8, 0.7, 0.6],  # 8
                       [0.5, 0.4, 0.4, 0.3]]]  # 9

            tabParam["MM"] = [[[1, 1, 1, 1],              # 0
                       [1, 1, 0.1, 0.1],              # 1
                       [1, 1, 0.1, 0.1],      # 2
                       [1, 0.8, 0.8, 0.4],      # 3
                       [1, 1, 1, 0.8],        # 4
                       [0.9, 0.9, 0.9, 0.8],  # 5
                       [0.7, 0.5, 0.5, 0.2],    # 6
                       [0.8, 0.6, 0.4, 0.2],      # 7
                       [0.9, 0.8, 0.7, 0.6],  # 8
                       [0.5, 0.4, 0.4, 0.3]]]  # 9

            tabParam["RM"] = [[[1, 1, 1, 1],              # 0
                       [1, 1, 0.1, 0.1],              # 1
                       [1, 1, 0.1, 0.1],      # 2
                       [1, 0.8, 0.6, 0.4],      # 3
                       [1, 1, 1, 0.8],        # 4
                       [0.9, 0.9, 0.9, 0.8],  # 5
                       [0.7, 0.5, 0.5, 0.2],    # 6
                       [0.8, 0.6, 0.4, 0.2],      # 7
                       [0.9, 0.8, 0.7, 0.6],  # 8
                       [0.5, 0.4, 0.4, 0.3]]]  # 9
            
            tab_justS = [[1,1,1],       # 0
                         [1,0,1],       # 1 : understand sound
                         [0,1,1],       # 2 : Don't have memory understand writing
                         [0,0,1],       # 3 
                         [0,1,1],       # 4 
                         [0,0.5,0.5],   # 5
                         [0.2,0.8,0.8], # 6 Don't have memory understand a bit writing
                         [1,0.5,1],     # 7
                         [0.8,0.8,1],   # 8 have memory and understant a bit writing
                         [0.7,0.7,0.9]] # 9 have a bit of both
            
            tab_showP = [[1,1],         # 0
                         [0,1],         # 1 understand ..E..
                         [1,0],         # 2 understand ..,.. E
                         [0.8,1],       # 3
                         [1,0.8],       # 4
                         [0.8,0.8],     # 5
                         [0.5,0.8],     # 6
                         [0.8,0.5],     # 7
                         [0.9,0.6],     # 8
                         [0.6,0.9],     # 9
                         [0.7,0.5],     # 10
                         [0.5,0.7]]     # 11
            
            tab_notesToken = [[1,1],        # 0
                              [0,1],        # 1 Don't know money but understant token
                              [1,0],        # 2 Know money and not token
                              [0.8,0.2],    # 3
                              [0.2,0.8],    # 4
                              [0.9,0.5],    # 5
                              [0.5,0.9],    # 6
                              [0.5,0.5],    # 7
                              [0.8,0.8]]    # 8

            tab_Car =         [[1,1],        # 0
                              [1,1],
                              [0.8,0.5],        # 2
                              [0.7,0.4],    # 3
                              [0.9,0.5],    # 5
                              [0.5,0.9],    # 6
                              [0.5,0.5],    # 7
                              [0.8,0.8]]    # 8

            tab_remainder = [[1,1],        # 0
                              [1,0.1],        # 2
                              [0.8,0.2],    # 3
                              [0.9,0.5],    # 5
                              [0.5,0.9],    # 6
                              [0.5,0.5],    # 7
                              [0.8,0.8]]    # 8

            tab_Holdremainder = [[[1, 1, 1, 1],              # 0
                       [1, 1, 0, 0],              # 1
                       [1, 0.3, 0.1, 0.1],      # 2
                       [1, 0.8, 0.6, 0.4],      # 3
                       [1, 1, 1, 0.8],        # 4
                       [0.9, 0.9, 0.9, 0.8],  # 5
                       [0.7, 0.5, 0.5, 0.2],    # 6
                       [0.8, 0.6, 0.4, 0.2],      # 7
                       [0.9, 0.8, 0.7, 0.6],  # 8
                       [0.5, 0.4, 0.4, 0.3]]]  # 9

            tabParam["mod"] = [tab_showP]
            tabParam["M4"] = [tab_notesToken]
            tabParam["Car"] = [tab_Car]
            tabParam["UR"] = [tab_remainder]
            tabParam["DR"] = [tab_remainder]
                              
            #tab_showS = [[1,1],
            #             [0.5,0.1],   # Don't know calcul without showing
             #            [0.8,0.1],   # //
              #           [1,0.1],     # //
               #          [0.8,0.4], 
                #         [1,0.7],
                 #        [1,0.9],
                  #       [0.5,0.5],
                   #      [0.8,0.8]]
            
            #tab.append(tab_showS)
            
            return tabParam

    # Function to filter if the param is on the size of the table     

# if __name__ == '__main__':
#     S = Student(0)
#     for ii in range(0,10):
#         print S.Answer([1,0,0,0],0,[])

#-*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        RandomSequence
# Purpose:
#
# Author:      Bclement
#
# Created:     14-03-2015
# Copyright:   (c) BClement 2015
# Licence:     GNU Affero General Public License v3.0

#-------------------------------------------------------------------------------
#from teacher_sequence import Sequence
from riarit import RiaritHssbg
import functions as func
#import random
import operator
import copy
import numpy as np

class RandomSequence(RiaritHssbg):

    def __init__(self, params = None,  params_file = "seq_test_1", directory = "params_files"):

        RiaritHssbg.__init__(self, params = params)
        self.generate_acts(**params["seq_path"])
        self.calcul_all_Ex_lvl()
        self.random_type = params["random_type"]

        return

    def sample(self, nb_stay = 0):
        if self.random_type == 0:
            r = random.randint(0,len(self.acts))
            return  self.acts[r]

        elif self.random_type == 1:
            return self.choose_lvl_random_ex()

        else:
            act = {}
            act = self.speSample(self.SSBGs[self.main_act],act,nb_stay)
            #self.lastAct = act
            return act

    def speSample(self,ssbgToS,act,nb_stay = 0):
        act[ssbgToS.ID] = ssbgToS.random_sample(nb_stay)
        for actRT in range(len(act[ssbgToS.ID])):
            nameRT = ssbgToS.param_values[actRT][act[ssbgToS.ID][actRT]]
            if nameRT[0:2] != 'NO':
                self.speSample(self.SSBGs[nameRT],act)
        return act
    
    def choose_lvl_random_ex(self):

        def dicht(dic,val):
            l = len(dic)/2
            if val < dic[l][1]:
                newDic = dic[:l]
            else:
                newDic = dic[l:]
            return newDic

        def calDist(val1,val2):
            return abs(val2 - val1)

        r = random.randint(0,100)
        r = 1.0*r/100
        newDic = copy.deepcopy(self.all_lvl)
        
        while len(newDic) > 3:
            newDic = dicht(newDic,r)

        dist = []
        for vals in newDic:
            dist.append(calDist(vals[1],r))

        exToChoose = newDic[dist.index(min(dist))]

        return self.acts[int(exToChoose[0])]

    def calcul_all_Ex_lvl(self):
        all_lvl = {}
        for i in range(len(self.acts)):
            all_lvl[str(i)] = np.mean(self.compute_act_lvl(self.acts[i],"MAIN"))
        self.all_lvl = sorted(all_lvl.items(), key=operator.itemgetter(1))
        #print sorted_lvl
        return 

    def generate_acts(self, params = None,  params_file = "expe_seq",directory = "sequence_def"):
        params = params or func.load_json(params_file,directory)
        self.acts = []
        for act_groups  in params["activity"]:
            for act in act_groups:
                self.acts.append(act)

        return

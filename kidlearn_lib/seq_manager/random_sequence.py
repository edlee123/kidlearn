#-*- coding: utf-8 -*-
from teacher_sequence import *
#import random
import operator
import copy

class Random_sequence(RIARIT_hssbg):

    def __init__(self,RT = None, levelupdate=0.6, filter1=0.1,filter2=0.9,uniformval=0.05, algo = "Random", path = None):

        RIARIT_hssbg.__init__(self, RT, levelupdate, filter1,filter2,uniformval,algo)
        #self.all_ex,self.all_lvl = 
        self.all_ExPossible()
        self.calcul_all_Ex_lvl()

        return

    def sample(self,sample_mod = 0,use_nb_turn = 0):
        if sample_mod == 0:
            r = random.randint(0,len(self.all_ex))
            return  self.all_ex[r]

        elif sample_mod == 1:
            return self.choose_lvl_random_ex

        else:
            act = {}
            act = self.speSample(self.SSBGs[self.mainName],act,use_nb_turn)
            self.lastAct = act
            return act

    def speSample(self,ssbgToS,act,use_nb_turn = 0):
        act[ssbgToS.ID] = ssbgToS.random_sample(self.lastAct,use_nb_turn)
        for actRT in range(len(act[ssbgToS.ID])):
            nameRT = ssbgToS.using_RT[actRT][act[ssbgToS.ID][actRT]]
            if nameRT[0:2] != 'NO':
                self.speRandom_Sample(self.SSBGs[nameRT],act)
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
            #print "NewTurn"
            #print newDic
            #print r
            newDic = dicht(newDic,r)
            #print newDic
            #raw_input()

        dist = []
        for vals in newDic:
            dist.append(calDist(vals[1],r))
        #print dist
        exToChoose = newDic[dist.index(min(dist))]
        #print exToChoose
        #raw_input()
        return self.all_ex[int(exToChoose[0])]

    def calcul_all_Ex_lvl(self):
        all_lvl = {}
        for i in range(len(self.all_ex)):
            all_lvl[str(i)] = mean(self.computelvl(self.all_ex[i],"MAIN"))
        self.all_lvl = sorted(all_lvl.items(), key=operator.itemgetter(1))
        #print sorted_lvl
        return 

    def all_ExPossible(self):
        self.all_ex = []
        self.all_ex.append({"MAIN" : [0], "M": [0]})
        self.all_ex.append({"MAIN" : [0], "M": [1]})
        self.all_ex.append({"MAIN" : [0], "M": [2]})

        self.all_ex.append({"MAIN" : [0], "M": [3], "mod": [0]})
        self.all_ex.append({"MAIN" : [0], "M": [3], "mod": [1]})
        self.all_ex.append({"MAIN" : [0], "M": [4], "mod": [0]})
        self.all_ex.append({"MAIN" : [0], "M": [4], "mod": [1]})
        self.all_ex.append({"MAIN" : [0], "M": [5], "mod": [0]})
        self.all_ex.append({"MAIN" : [0], "M": [5], "mod": [1]})

        self.all_ex.append({"MAIN" : [1], "R": [0]})
        self.all_ex.append({"MAIN" : [1], "R": [1]})

        self.all_ex.append({"MAIN" : [1], "R": [2], "mod": [0]})
        self.all_ex.append({"MAIN" : [1], "R": [2], "mod": [1]})
        self.all_ex.append({"MAIN" : [1], "R": [3], "mod": [0]})
        self.all_ex.append({"MAIN" : [1], "R": [3], "mod": [1]})

        self.all_ex.append({"MAIN" : [2], "MM": [0], "UR": [0]})
        self.all_ex.append({"MAIN" : [2], "MM": [0], "UR": [1]})
        self.all_ex.append({"MAIN" : [2], "MM": [1], "UR": [0]})
        self.all_ex.append({"MAIN" : [2], "MM": [1], "UR": [1]})

        self.all_ex.append({"MAIN" : [2], "MM": [2], "Car": [0], "UR": [0]})
        self.all_ex.append({"MAIN" : [2], "MM": [2], "Car": [0], "UR": [1]})
        self.all_ex.append({"MAIN" : [2], "MM": [2], "Car": [1], "DR": [0]})
        self.all_ex.append({"MAIN" : [2], "MM": [2], "Car": [1], "DR": [1]})

        self.all_ex.append({"MAIN" : [2], "MM": [3], "M4": [0], "Car": [0], "UR": [0]})
        self.all_ex.append({"MAIN" : [2], "MM": [3], "M4": [0], "Car": [0], "UR": [1]})
        self.all_ex.append({"MAIN" : [2], "MM": [3], "M4": [1], "Car": [0], "UR": [0]})
        self.all_ex.append({"MAIN" : [2], "MM": [3], "M4": [1], "Car": [0], "UR": [1]})
        self.all_ex.append({"MAIN" : [2], "MM": [3], "M4": [0], "Car": [1], "DR": [0]})
        self.all_ex.append({"MAIN" : [2], "MM": [3], "M4": [0], "Car": [1], "DR": [1]})
        self.all_ex.append({"MAIN" : [2], "MM": [3], "M4": [1], "Car": [1], "DR": [0]})
        self.all_ex.append({"MAIN" : [2], "MM": [3], "M4": [1], "Car": [1], "DR": [1]})

        self.all_ex.append({"MAIN" : [3], "RM": [0], "UR": [0]})
        self.all_ex.append({"MAIN" : [3], "RM": [0], "UR": [1]})
        self.all_ex.append({"MAIN" : [3], "RM": [1], "UR": [0]})
        self.all_ex.append({"MAIN" : [3], "RM": [1], "UR": [1]})

        self.all_ex.append({"MAIN" : [3], "RM": [2], "Car": [0], "UR": [0]})
        self.all_ex.append({"MAIN" : [3], "RM": [2], "Car": [0], "UR": [1]})
        self.all_ex.append({"MAIN" : [3], "RM": [2], "Car": [1], "DR": [0]})
        self.all_ex.append({"MAIN" : [3], "RM": [2], "Car": [1], "DR": [1]})

        self.all_ex.append({"MAIN" : [3], "RM": [3], "M4": [0], "Car": [0], "UR": [0]})
        self.all_ex.append({"MAIN" : [3], "RM": [3], "M4": [0], "Car": [0], "UR": [1]})
        self.all_ex.append({"MAIN" : [3], "RM": [3], "M4": [0], "Car": [1], "DR": [0]})
        self.all_ex.append({"MAIN" : [3], "RM": [3], "M4": [0], "Car": [1], "DR": [1]})
        self.all_ex.append({"MAIN" : [3], "RM": [3], "M4": [1], "Car": [0], "UR": [0]})
        self.all_ex.append({"MAIN" : [3], "RM": [3], "M4": [1], "Car": [0], "UR": [1]})
        self.all_ex.append({"MAIN" : [3], "RM": [3], "M4": [1], "Car": [1], "DR": [0]})
        self.all_ex.append({"MAIN" : [3], "RM": [3], "M4": [1], "Car": [1], "DR": [1]})

        return 

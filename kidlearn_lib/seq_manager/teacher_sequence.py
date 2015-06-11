#-*- coding: utf-8 -*-
import os
import sys
from numpy import *
import copy
import re
from zpdes import *
import copy

class Sequence(RIARIT_hssbg):
     
    def __init__(self,RT = None, levelupdate=0.6, filter1=0.1,filter2=0.9,uniformval=0.05,sizeSerie = 6, path = "hierarchyRT/RT_", params = {}):

        sizeSerie = params['sizeSerie']
        RIARIT_hssbg.__init__(self, RT, levelupdate, filter1,filter2,uniformval, path, params = params)
        #self.fault = [0]*sizeSerie utsing ?
        self.generate_acts()
        self.answers = [0]*sizeSerie
        self.seqLevels = [0]*len(self.acts)
        self.currentGroup = 0
        self.num_question = 0
        self.nbPoint = 0
        self.toLvlYp = params['toLvlYp']
        self.minAns = params['minAns'] 
        #self.ssbh = ZPDES_hssbg(RT, levelupdate, filter1, filter2, uniformval, algo = "RiARiT")
        return

    def getSeqLevel(self):
        return self.seqLevels

    def reinit(self,ans,lvls,cGroup,nQuestion, nbPoint):
        self.answers = ans
        self.seqLevels = lvls
        self.currentGroup = cGroup
        self.num_question = nQuestion
        self.nbPoint = nbPoint
        return

    def resetLevel(self):
        self.answers = [0]*len(self.answers)
        self.num_question = 0
        self.nbPoint = 0

    def lvlup(self):
        if self.seqLevels[self.currentGroup] < len(self.acts[self.currentGroup])-1 :
            self.seqLevels[self.currentGroup] = self.seqLevels[self.currentGroup] +1
            self.resetLevel();
        else:
            self.changeGroup()

    def changeGroup(self):
        self.currentGroup +=1
        if self.currentGroup == len(self.acts):
            self.currentGroup = 0
            #self.seqLevels = [0]*len(self.acts)
        self.resetLevel();

    def update(self,act = None, corsol = True, nbFault = 0, *args, **kwargs):
        RIARIT_hssbg.update(self,act,corsol)
        #print " Answer %s" % self.answers
        #print "corsol %s" % corsol
        #print "nbFaul %s" % nbFault
        if corsol:
            self.answers[self.num_question] = 1
            self.nbPoint += max(5 - nbFault,3)
        #consecutive = 0
        #if(self.num_question > 0):
         #   consecutive = self.answers[self.num_question]+self.answers[self.num_question-1]
        self.num_question += 1
        #print "nbpoint %s" % self.nbPoint
        if self.nbPoint >= self.toLvlYp and self.num_question == len(self.answers):#self.minAns:
            #print self.answers
            #print self.nbPoint
            #raw_input()
            self.lvlup();

        #I made changement here

        elif self.num_question == len(self.answers) and sum(self.answers) < self.toLvlYp - self.toLvlYp/3.0:
            self.changeGroup()

        elif self.num_question == len(self.answers):
            self.resetLevel()

        #print "CGroup : %s" % self.currentGroup
        #print " SeqLevels %s" % self.seqLevels
        #print " Answer %s" % self.answers
        #print " NQ %s" % self.num_question
        #raw_input()

    def sample(self):
        act = copy.deepcopy(self.acts[self.currentGroup][self.seqLevels[self.currentGroup]])
        return act

    def generate_acts(self,nGroup = 5):
        self.acts = [[] for x in range(nGroup)]
        """
        self.acts.append([0,2,1,0]);
        self.acts.append([1,2,1,0]);
        self.acts.append([1,0,1,0]);
        self.acts.append([2,2,1,0]);
        self.acts.append([2,0,1,0]);
        self.acts.append([3,2,1,0]);
        self.acts.append([3,2,0,0]);
        self.acts.append([3,1,0,0]);
        self.acts.append([4,1,0,0]);
        self.acts.append([5,1,1,0]);
        #"""
        self.acts[0].append({"MAIN" : [0], "M": [0]})#, "mod": [0]})
        self.acts[0].append({"MAIN" : [0], "M": [1]})#, "mod": [0]})
        self.acts[0].append({"MAIN" : [0], "M": [2]})#, "mod": [0]})
        #self.acts[0].append({"MAIN" : [0], "M": [2], "mod": [1]})
        
        self.acts[1].append({"MAIN" : [0], "M": [3], "mod": [0]})
        self.acts[1].append({"MAIN" : [0], "M": [4], "mod": [0]})
        self.acts[1].append({"MAIN" : [0], "M": [4], "mod": [1]})
        self.acts[1].append({"MAIN" : [0], "M": [5], "mod": [1]})

        self.acts[2].append({"MAIN" : [1], "R": [0]})#, "mod": [0]})
        self.acts[2].append({"MAIN" : [1], "R": [1]})#, "mod": [0]})

        self.acts[2].append({"MAIN" : [1], "R": [2], "mod": [0]})
        #self.acts[2].append({"MAIN" : [1], "R": [2], "mod": [1]})
        self.acts[2].append({"MAIN" : [1], "R": [2], "mod": [0]})
        self.acts[2].append({"MAIN" : [1], "R": [3], "mod": [1]})

        self.acts[3].append({"MAIN" : [2], "MM": [0], "UR": [0]})
        self.acts[3].append({"MAIN" : [2], "MM": [0], "UR": [1]})
        self.acts[3].append({"MAIN" : [2], "MM": [1], "UR": [0]})
        self.acts[3].append({"MAIN" : [2], "MM": [1], "UR": [1]})

        self.acts[3].append({"MAIN" : [2], "MM": [2], "Car": [0], "UR": [0]})
        self.acts[3].append({"MAIN" : [2], "MM": [2], "Car": [0], "UR": [1]})
        self.acts[3].append({"MAIN" : [2], "MM": [3], "M4": [0], "Car": [1], "DR": [0]})
        self.acts[3].append({"MAIN" : [2], "MM": [3], "M4": [1], "Car": [1], "DR": [1]})

        self.acts[4].append({"MAIN" : [3], "RM": [0], "UR": [0]})
        self.acts[4].append({"MAIN" : [3], "RM": [0], "UR": [1]})
        self.acts[4].append({"MAIN" : [3], "RM": [1], "UR": [0]})
        self.acts[4].append({"MAIN" : [3], "RM": [1], "UR": [1]})

        self.acts[4].append({"MAIN" : [3], "RM": [2], "Car": [0], "UR": [0]})
        self.acts[4].append({"MAIN" : [3], "RM": [2], "Car": [0], "UR": [1]})
        self.acts[4].append({"MAIN" : [3], "RM": [3], "M4": [0], "Car": [1], "DR": [0]})
        self.acts[4].append({"MAIN" : [3], "RM": [3], "M4": [1], "Car": [1], "DR": [1]})
        
        return
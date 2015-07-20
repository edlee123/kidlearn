#-*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        teacher_sequence
# Purpose:     
#
# Author:      Bclement
#
# Created:     14-03-2015
# Copyright:   (c) BClement 2015
# Licence:     GNU Affero General Public License v3.0
#-------------------------------------------------------------------------------

import os
import sys
from numpy import *
import copy
import re
from zpdes import *
import copy
import functions as func
import collections

class Sequence(RiaritHssbg):
     
    def __init__(self,params = None,  params_file = "seq_test_1", directory = "params_files"):

        sizeSerie = params['sizeSerie']
        RiaritHssbg.__init__(self, params = params)
        #self.fault = [0]*sizeSerie utsing ?
        self.generate_acts(**params["seq_path"])
        self.answers = [0]*sizeSerie
        self.seqLevels = [0]*len(self.acts)
        self.currentGroup = 0
        self.num_question = 0
        self.nbPoint = 0
        self.toLvlYp = params['toLvlYp']
        self.minAns = params['minAns'] 
        #self.ssbh = ZpdesHssbg(RT, levelupdate, filter1, filter2, uniformval, algo = "RiARiT")
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
        RiaritHssbg.update(self,act,corsol)
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

    def generate_acts(self, params = None,  params_file = "expe_seq",directory = "sequence_def"):
        params = params or func.load_json(params_file,directory)
        self.acts = []
        #seq_dict = collections.OrderedDict(params["activity"])
        #for key,act_groups  in params["activity"].items():
        for act_groups  in params["activity"]:
            self.acts.append(act_groups)

        return
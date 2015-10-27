#-*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        HierarchicalSSBG
# Purpose:     Hieratical Strategic Student Bandit
#
# Author:      Bclement
#
# Created:     14-03-2015
# Copyright:   (c) BClement 2015
# Licence:     GNU Affero General Public License v3.0
#-------------------------------------------------------------------------------

import os
import sys
import re
import pickle
import json
import numpy as np

from .. import functions as func


#########################################################
#########################################################
#########################################################
## class HierarchicalSSBG

class HierarchicalSSBG(object):

    def __init__(self, params=None, params_file="seq_test_1", directory="params_files"):
        # params : RT, path

        self.params = params

        #main_dir = self.params["path"]
        #path = main_dir+self.params["path_RT"]
        self.graph_path = self.params["graph"]["path"]
        self.main_act = self.params["graph"]["main_act"]
        
        self.ssbg_used = []
        #RT = {"name": self.main_act, "path": self.graph_path}
        #RT = "%s/%s.txt" % (self.graph_path, self.main_act)
        self.CreateHSSBG(self.params["graph"])

        return

    def get_state(self):
        state = {}
        state["bandval"] = self.getBanditValue()
        
        return state

    def getRTnames(self):
        return self.SSBGs.keys()

    def getNbValueParam(self):
        nbValueParam = {}
        for RT in self.SSBGs.keys():
            nbValueParam[RT] = []
            for ssb in self.SSBGs[RT].SSB:
                nbValueParam[RT].append(len(ssb.bandval))
        return nbValueParam

    def getSuccess(self):
        success = {}
        for RT,ssbg in self.SSBGs.items():
            success[RT] = ssbg.getSuccess()
        return success
    
    def setSuccess(self, successTab):
        for RT,ssbg in self.SSBGs.items():
            ssbg.setSuccess(successTab[RT])
        return


    def getBanditValue(self):
        banditVal = {}
        for RT,ssbg in self.SSBGs.items():
            banditVal[RT] = ssbg.getBanditValue()
        return banditVal

    def setBanditValue(self, banditTab):
        for RT,ssbg in self.SSBGs.items():
            ssbg.setBanditValue(banditTab[RT])
        return

    def instantiate_ssbg(self):
        return SSBanditGroup(params=self.params["SSBanditGroup"])
        #return self.ssbgClasse(RT, params = self.params)

    def CreateHSSBG(self, seq_graph):
        mainSSBG = self.instantiate_ssbg(seq_graph)
        self.ncompetences = mainSSBG.ncompetences
        self.SSBGs = {}
        self.SSBGs[self.main_act] = mainSSBG
        self.addSSBG(mainSSBG)
        #self.lastAct = {}
        return

    def addSSBG(self, ssbg_father):
        for actRT,hierarchy,i in zip(ssbg_father.param_values,ssbg_father.values_children ,range(len(ssbg_father.param_values))):
            for nameRT,hierar in zip(actRT,hierarchy) :
                if hierar and nameRT not in self.SSBGs.keys():
                    RT = {"name": nameRT, "path": self.graph_path}
                    #RT = "%s/%s.txt" % (self.graph_path, nameRT)
                    nssbg = self.instantiate_ssbg(RT)
                    self.SSBGs[nameRT] = nssbg
                    ssbg_father.add_sonSSBG(i,self.SSBGs[nameRT])
                    self.addSSBG(nssbg)

    def update(self, act=None, result=True, error_ID=None, *args, **kwargs):
        return 0

    def sample(self):
        act = self.speSample(ssbgToS = self.SSBGs[self.main_act])
        #self.lastAct = act
        return act

    def speSample(self, ssbgToS, act=None):
        if act is None: act = {}
        act[ssbgToS.ID] = ssbgToS.sample()
        for actRT in range(len(act[ssbgToS.ID])):
            hierar = ssbgToS.values_children[actRT][act[ssbgToS.ID][actRT]]
            if hierar:
                nameRT = ssbgToS.param_values[actRT][act[ssbgToS.ID][actRT]]
                self.speSample(self.SSBGs[nameRT],act)
        return act

## class HierarchicalSSBG
#########################################################

#########################################################
#########################################################
#########################################################
## class SSBanditGroup

class SSBanditGroup(object):

    def __init__(self, params=None, params_file="ssb_test_1", directory="params_files"):
        #params : RT
        self.params = params
        #self.sonSSBG = {}

        return

    def __repr__(self):
        return self.ID

    def getSuccess(self):
        successSSBG = []
        for i in range(len(self.SSB)):
            successSSBG.append(self.SSB[i].getSuccess())
        return successSSBG

    def setSuccess(self, tabSuccess):
        for i in range(len(tabSuccess)):
            self.SSB[i].setSuccess(tabSuccess[i])
        return

    def getBanditValue(self):
        banditVal = []
        for i in range(len(self.SSB)):
            banditVal.append(self.SSB[i].getBanditValue())
        return banditVal

    def setBanditValue(self, banditTab):
        for i in range(len(banditTab)):
            self.SSB[i].setBanditValue(banditTab[i])
        return

    def testRT(self):
        tested = [False]*self.nactions
        return

    def add_sonSSBG(self, nact, sonSSBG):
        for ssb in sonSSBG.SSB:
            if ssb.is_hierarchical == 1:
                self.SSB[nact].add_sonSSBG(sonSSBG)
                break
        return

    def loadRT(self):
        return

    def instanciate_ssb(self, ii, is_hierarchical):
        return SSbandit(ii,len(self.RT[ii]),self.ncompetences,is_hierarchical, param_values = self.param_values[ii], params = self.params)

    def CreateSSBs(self):
        self.SSB = [[] for i in range(self.nactions)]
        for ii in range(0,len(self.SSB)):
            self.SSB[ii] = self.instanciate_ssb(ii,self.h_actions[ii])
        return

    def update(self, act, r):
        return

    def calcul_reward(self):
        return 0

    def random_sample(self, nb_stay=None):
        for i in range(self.nactions):
            nb_stay = nb_stay or self.nb_stay[i]
            if self.nbturn[i] % nb_stay == 0:
                self.act[i] = int(self.SSB[i].random_sample())
                self.nbturn[i] = 0
        return self.act

    def sample(self):
        for i in range(self.nactions):
            if self.nbturn[i] % self.nb_stay[i] == 0:
                self.act[i] = int(self.SSB[i].sample())
                self.nbturn[i] = 0
        return self.act

#HierarchicalSSBG.ssbgClasse = SSBanditGroup

## class SSBanditGroup
#########################################################

#########################################################
#########################################################
#########################################################
## class SSbandit

class SSbandit(object):
    """Strategic Student Bandit"""

    def __init__(self, id, nval, is_hierarchical=0, param_values=None, params=None):
        if param_values is None : param_values = []
        if params is None : params = {}
        # params : filter1, filter2, uniformval,

        self.params = params
        self.id = id
        self.nval = nval
        self.bandval = [0]*nval
        
        self.filter1 = params["filter1"]
        self.filter2 = 1 - params["filter1"]
        self.uniformval = params["uniformval"]

        self.success = [[] for x in xrange(nval)]
        self.is_hierarchical = is_hierarchical
        self.param_values = param_values
        self.sonSSBG = {}
        self.name = "ssb"
        return

    def getSuccess(self):
        return self.success

    def setSuccess(self, tabSuccess):
        self.success = tabSuccess
        return

    def getBanditValue(self):
        return self.bandval

    def setBanditValue(self, banditTab):
        self.bandval = banditTab
        return

    def add_sonSSBG(self, sonSSBG):
        self.sonSSBG[sonSSBG.ID] = sonSSBG
        return

    def plot(self):
        print self.bandval
        return

    def update(self, val, r):
        self.bandval[val] = self.filter1*self.bandval[val] + self.filter2*r

    def promote(self):
        return

    def random_sample(self):
        nn = [1.0/self.nval]*self.nval
        return func.dissample(nn)

    def sample(self, exploration_coeff=10):
        
        nn = np.array(self.bandval)
        norm_v = sum(nn)
        for i in range(0,len(nn)) :
            if nn[i] > 0 :
                nn[i] = nn[i] + norm_v/exploration_coeff
    
        nb_0 = 0
        for i in range(0,len(nn)) :
            if nn[i] < pow(10,-70) :
                nb_0 += 1
        
        if nb_0 == len(nn):
            print self.name
            print "Prob : %s : %s " % (str(self.param_values),str(self.bandval))
            #print self.success
        #nn = exp(nn)-1
        nn = nn/sum(nn)
        
        """
        nb_0 = 0
        for i in range(0,len(nn)) :
            if nn[i] < 1.0/(pow(10,50)) :
                nb_0 += 1
        if nb_0 == len(nn):
            print "band : %s " % str(nn)
        """
        return func.dissample(nn)


## class SSbandit
#########################################################
#-*- coding: utf-8 -*-
## Hieratical Strategic Student Bandit
## 2014 BCLEMENT

from numpy import *
import re
import pickle
import json

""" auxiliary functions """
def dissample(p):
    s = random.multinomial(1,p)
    return nonzero(s==1)[0][0]


#########################################################
#########################################################
#########################################################
## class HierachySSBG
class HierarchySSBG(object):
    def __init__(self,RT = "MAIN", filter1=None,filter2=None,uniformval=None, path = ""):
        self.filter1 = filter1
        self.filter2 = filter2
        self.uniformval = uniformval
        self.ssbg_used = []
        #self.current_lvl_ex = {}
        self.algo = "HierarchySSBG"
        self.path = path
        self.main_act = RT
        RT = self.path + RT+".txt"
        self.CreateHSSBG(RT)

        return

    def get_state(self):
        state = {}
        #state["success_rate"] = self.getSuccess()
        state["bandval"] = self.getBanditValue()
        #state[""]
        
        return state

    #def get_bandval(self):
    #    bandval = {}
    #    for nameRT,ssbg in self.SSBGs.items():
    #        bandval[nameRT] = [] 
    #        for i in range(len(ssbg.SSB)):
    #            bandval[nameRT].append(copy.copy(ssbg.SSB[i].bandval))
    #    return bandval

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
    
    def setSuccess(self,successTab):
        for RT,ssbg in self.SSBGs.items():
            ssbg.setSuccess(successTab[RT])
        return


    def getBanditValue(self):
        banditVal = {}
        for RT,ssbg in self.SSBGs.items():
            banditVal[RT] = ssbg.getBanditValue()
        return banditVal

    def setBanditValue(self,banditTab):
        for RT,ssbg in self.SSBGs.items():
            ssbg.setBanditValue(banditTab[RT])
        return

    def instantiate_ssbg(self,RT):
        return SSBanditGroup(RT,self.filter1,self.filter2,self.uniformval,algo = self.algo)

    def CreateHSSBG(self,RT = 'assets/algorithm/hierarchyRT/RT_MAIN.txt'):
        mainSSBG = self.instantiate_ssbg(RT)
        self.ncompetences = mainSSBG.ncompetences
        self.SSBGs = {}
        self.SSBGs[self.main_act] = mainSSBG
        self.addSSBG(mainSSBG)
        #self.lastAct = {}
        return

    def addSSBG(self,ssbg_father):
        for actRT,i in zip(ssbg_father.using_RT,range(len(ssbg_father.using_RT))):
            for nameRT in actRT :
                if nameRT[0:2] != 'NO' and nameRT not in self.SSBGs.keys():
                    RT = self.path + nameRT+".txt"
                    nssbg = self.instantiate_ssbg(RT)
                    self.SSBGs[nameRT] = nssbg
                    ssbg_father.add_sonSSBG(i,self.SSBGs[nameRT])
                    self.addSSBG(nssbg)
        return

    def update(self, act = None, corsol = True, error_ID = None, *args, **kwargs):

        return 0


    def sample(self):
        act = {}
        act = self.speSample(self.SSBGs[self.main_act],act)
        #self.lastAct = act
        return act

    def speSample(self,ssbgToS,act): 
        act[ssbgToS.ID] = ssbgToS.sample()
        for actRT in range(len(act[ssbgToS.ID])):
            nameRT = ssbgToS.using_RT[actRT][act[ssbgToS.ID][actRT]]
            if nameRT[0:2] != 'NO':
                self.speSample(self.SSBGs[nameRT],act)
        return act

## class HierachySSBG
#########################################################

#########################################################
#########################################################
#########################################################
## class SSBanditGroup
class SSBanditGroup(object):
    def __init__(self, RT, filter1,filter2,uniformval,algo):
        self.filter1 = filter1
        self.filter2 = filter2
        self.uniformval = uniformval
        self.algo = algo
        #self.sonSSBG = {}
        self.loadRT(RT)

        return

    def __repr__(self):
        return self.ID
    def __str__(self):
        return self.ID

    def getSuccess(self):
        successSSBG = []
        for i in range(len(self.SSB)):
            successSSBG.append(self.SSB[i].getSuccess())
        return successSSBG

    def setSuccess(self,tabSuccess):
        for i in range(len(tabSuccess)):
            self.SSB[i].setSuccess(tabSuccess[i])
        return

    def getBanditValue(self):
        banditVal = []
        for i in range(len(self.SSB)):
            banditVal.append(self.SSB[i].getBanditValue())
        return banditVal

    def setBanditValue(self,banditTab):
        for i in range(len(banditTab)):
            self.SSB[i].setBanditValue(banditTab[i])
        return

    def testRT(self):
        tested = [False]*self.nactions
        return

    def add_sonSSBG(self,nact,sonSSBG):
        #self.sonSSBG[sonSSBG.ID] = sonSSBG
        for ssb in sonSSBG.SSB:
            if ssb.is_hierarchical == 1:
                self.SSB[nact].add_sonSSBG(sonSSBG)
                break
        return

    def loadRT(self):
        return

    def instanciate_ssb(self,ii,is_hierarchical):
        return SSbandit(ii,len(self.RT[ii]),self.ncompetences,self.requer[ii], self.stop[ii],self.filter1,self.filter2,self.uniformval, self.algo,is_hierarchical, using_RT = self.using_RT[ii])

    def CreateSSBs(self):
        self.SSB = [[] for i in range(self.nactions)]
        for ii in range(0,len(self.SSB)):
            is_hierarchical = (self.actions[ii][-1] == "H")
            self.SSB[ii] = self.instanciate_ssb(ii,is_hierarchical)
        return

    def update(self,act,r):
        return

    def calcul_reward(self):
        return 0

    def sample(self):
        for i in range(self.nactions):
            if self.nbturn[i] % self.nb_stay[i] == 0:
                self.act[i] = int(self.SSB[i].sample())
                self.nbturn[i] = 0
        return self.act


## class SSBanditGroup
#########################################################

#########################################################
#########################################################
#########################################################
## class SSbandit
class SSbandit(object):
    """Strategic Student Bandit"""

    def __init__(self,id, nval, ntask, filter1,filter2,uniformval, algo,is_hierarchical = 0, using_RT = []):

        self.id = id
        self.nval = nval
        self.bandval = [0]*nval
        self.filter1 = filter1
        self.filter2 = filter2
        self.uniformval = uniformval
        self.algo = algo
        self.success = [[] for x in xrange(nval)]
        self.is_hierarchical = is_hierarchical
        self.using_RT = using_RT
        self.sonSSBG = {}
        return

    def getSuccess(self):
        return self.success

    def setSuccess(self,tabSuccess):
        self.success = tabSuccess
        return

    def getBanditValue(self):
        return self.bandval

    def setBanditValue(self,banditTab):
        self.bandval = banditTab
        return

    def add_sonSSBG(self,sonSSBG):
        self.sonSSBG[sonSSBG.ID] = sonSSBG
        return

    def plot(self):
        print self.bandval
        return

    def update(self,val,r):
        self.bandval[val] = self.filter1*self.bandval[val] + self.filter2*r

    def promote(self):
        return

    def sample(self, exploration_coeff = 10):
        
        nn = array(self.bandval)
        norm_v = sum(nn)
        for i in range(0,len(nn)) :
            if nn[i] > 0 :
                nn[i] = nn[i] + norm_v/exploration_coeff
    
        nb_0 = 0
        for i in range(0,len(nn)) :
            if nn[i] < pow(10,-30) :
                nb_0 += 1
        
        if nb_0 == len(nn):
            print self.algo
            print "Prob : %s : %s " % (str(self.using_RT),str(nn))
            print self.bandval
            print self.success
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
        return dissample(nn)



## class SSbandit
#########################################################

def spe_split(regex,line):
    tmp=re.split(regex,line)
    tmp = [x for x in tmp if x not in [None,'']]
    return tmp
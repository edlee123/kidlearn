#-*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        riarit
# Purpose:     Right Activity at the Right Time
#
# Author:      Bclement
#
# Created:     14-03-2015
# Copyright:   (c) BClement 2015
# Licence:     GNU Affero General Public License v3.0
#-------------------------------------------------------------------------------

import os
import numpy as np

from .hssbg import HierarchicalSSBG,SSBanditGroup, SSbandit
from ..functions import functions as func

#########################################################
#########################################################
## class RIARIT_hssb

class RiaritHssbg(HierarchicalSSBG):

    def __init__(self, params=None, params_file="seq_test_1", directory="params_files"):
        # params : RT, path

        params = params or func.load_json(params_file,directory)
        self.current_lvl_ex = {}
        params["graph"] = params["RT"]
        HierarchicalSSBG.__init__(self, params=params)
        self.load_Error()
        #self.CreateHSSBG(RT)

    # Accesser
    def get_KC(self):
        return self.SSBGs[self.main_act].competences

    def get_state(self):
        state = HierarchicalSSBG.get_state(self)
        state["estim_lvl"] = self.get_estim_level(self.main_act, dict_form = 1)
        return state

    def get_estim_level(self,RT="", *args, **kwargs):
        level = {}
        for nameRT,ssbg in self.SSBGs.items():
            level[nameRT] = ssbg.get_estim_level(**kwargs)
        if RT != "":
            return {RT : level[RT]}
        return level

    def setLevel(self, levels):
        for RT,lvl in levels.items():
            self.SSBGs[RT].setLevel(lvl)
        return

    #Ssbg define
    def instantiate_ssbg(self, RT):
        params = self.params["RiaritSsbg"]
        params["RT"] = RT
        return RiaritSsbg(params=params)

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
                elif hierar:
                    ssbg_father.add_sonSSBG(i,self.SSBGs[nameRT])
        return

    # RiaRit spe func
    def compute_act_lvl(self, act, RT=None, **kwargs):
        lvl = {}
        lvl[self.main_act] = [1]*self.ncompetences
        self.ssbg_used = []
        self.ssbg_used.append(self.main_act)
        lvl = self.addSsbgToCompute(self.SSBGs[self.main_act],act, **kwargs)
        self.current_lvl_ex[self.main_act] = lvl
        if RT != None:
            if RT == "main":
                return self.current_lvl_ex[self.main_act]
            else:
                return self.current_lvl_ex[RT]
        return self.current_lvl_ex

    def addSsbgToCompute(self, pre_ssbg, act, lvl=None, **kwargs):
        #if lvl == None:
        #    lvl = [1]*self.ncompetences
        #print pre_ssbg.ID
        #print act
        for actRT in range(len(pre_ssbg.param_values)):
            hierar = pre_ssbg.values_children[actRT][act[pre_ssbg.ID][actRT]]
            if hierar:
                nameRT = pre_ssbg.param_values[actRT][act[pre_ssbg.ID][actRT]]
                self.ssbg_used.append(nameRT)
                lvl = self.addSsbgToCompute(self.SSBGs[nameRT],act,lvl, **kwargs)

        lvl = pre_ssbg.RTable(act[pre_ssbg.ID],lvl, **kwargs)
        self.current_lvl_ex[pre_ssbg.ID] = lvl
        pre_ssbg.ID

        return lvl


    def update(self, act, corsol=True, error_ID=None, *args, **kwargs):
        #if act is None:
        #    act = self.lastAct
        #self.computelvl(act)

        answer_impact = self.return_answer_impact(corsol,error_ID)

        for nameRT in act.keys():
            self.SSBGs[nameRT].update(self.current_lvl_ex[nameRT],act[nameRT], corsol, answer_impact)
        return

    # Special func to try to take into account error
    def load_Error(self, RT_ID="MAIN", directory='assets/algorithm/error_RT/'):
        self.error_tab = []
        self.error_ID_tab = []
        file_to_read = "%serror_%s%s" % (directory,RT_ID,".txt")
        try:
            reader = open(file_to_read, 'rb')
            lines = reader.readlines()
            for lin in lines[2:]:
                tmp = func.spe_split('\s(\d*\.\d*|\d+)|\s([a-zA-Z0-9_]*)',lin)
                aux = [float(x) for x in tmp[2:len(tmp)]]
                self.error_ID_tab.append(tmp[1])
                self.error_tab.append(aux[0:self.ncompetences])
        except:
            return
        return

    def return_answer_impact(self, corsol, error_ID=None):
        if corsol == 1:
            return [1]*max(1,self.ncompetences)
        elif error_ID != None:
            error_num = self.error_ID_tab.index(error_ID)
        else:
            return [0]*max(1,self.ncompetences)

        return self.error_tab[error_num]

## class RIARIT_hssb
#########################################################

#########################################################
#########################################################
## class RiaritSsbg
class RiaritSsbg(SSBanditGroup):

    def __init__(self, params=None, params_file="Rssb_test_1", directory="params_files"):
        SSBanditGroup.__init__(self,params=params)

        self.loadRT(self.params["RT"])
        self.levelupdate = self.params["levelupdate"]
        
        return

    def instanciate_ssb(self, ii, is_hierarchical):
        params = self.params["RiaritSsb"]

        return RiaritSsb(ii,self.nvalue[ii],self.ncompetences,self.requer[ii], self.stop[ii], is_hierarchical=is_hierarchical, param_values=self.param_values[ii], params=params)

    def get_estim_level(self, **kwargs):
        if "dict_form" in kwargs.keys():
            return {key: value for (key,value) in zip(self.competences,self.estim_level)}
        return self.estim_level

    def setLevel(self, level):
        self.estim_level = level

    def calDiffLvl(self, lvl):
        lvlDiff = []
        for i in range(self.ncompetences):
            lvlDiff.append(lvl[i]-self.estim_level[i])
        return lvlDiff
    
    def loadRT(self, RT):
        if os.path.exists(os.path.join(RT["path"],RT["name"]+".json")):
            self.load_jsonRT(RT)
        else:
            self.load_textRT(RT)
        self.CreateSSBs()

    def load_jsonRT(self, RT):
        self.ID = RT["name"]
        params_RT = func.load_json(RT["name"],RT["path"])
        self.competences = params_RT["competencies"]
        self.ncompetences = len(self.competences)
        self.estim_level = [0]*self.ncompetences
        self.actions = params_RT["parameters"]
        self.nactions = len(self.actions)
        self.act = [0]*self.nactions
        self.h_actions = [0]*self.nactions
        self.nbturn = [0]*self.nactions
        self.nb_stay = func.fill_data(params_RT["nb_stay"],self.nactions)
        #self.nb_stay = params_RT["nb_stay"] + [params_RT["nb_stay"][-1]]*(self.nactions-(len(params_RT["nb_stay"])-1))
        self.RT = [[] for i in range(self.nactions)]
        self.requer = [[] for i in range(self.nactions)]
        self.stop = [[] for i in range(self.nactions)]
        self.param_values = [[] for i in range(self.nactions)]
        self.values_children = [[] for i in range(self.nactions)]
        self.nvalue = []
        for num_act in range(self.nactions):
            for key,val in params_RT["table"][self.actions[num_act]].items():
                self.param_values[num_act].append(key)
                if "hierarchical" in val.keys():
                    self.values_children[num_act].append(int(val["hierarchical"]))
                else:
                    self.values_children[num_act].append(0)

                self.RT[num_act].append(val["impact"])
                self.requer[num_act].append(func.fill_data(val["requir"],self.ncompetences))
                self.stop[num_act].append(func.fill_data(val["deacti"],self.ncompetences))
            self.nvalue.append(len(self.param_values[num_act]))

    def load_textRT(self, RT):
        path_RT = os.path.join(RT["path"],RT["name"])+".txt"
        reader = open(path_RT, 'rb')
        self.ID = ((path_RT.split("/")[-1]).split(".")[0])
        #self.ID = ((path_RT.split("/")[-1]).split(".")[0]).split("_")[1]
        #print "SSB CREATE: %s" % self.ID
        lines = reader.readlines()
        tmp = func.spe_split('\W',lines[0])
        self.competences = tmp[1:len(tmp)]
        self.ncompetences = len(self.competences)
        self.estim_level = [0]*self.ncompetences

        tmp = func.spe_split('\W',lines[1])
        self.actions = tmp[1:len(tmp)]
        self.nactions = len(self.actions)
        self.act = [0]*self.nactions
        self.h_actions = [ int(x[-1] == "H") for x in self.actions]
        self.nbturn = [0]*self.nactions

        tmp = func.spe_split('\W',lines[2])
        self.nb_stay = [int(x) for x in tmp[1:len(tmp)]] + [int(x)]*(self.nactions-(len(tmp)-1))

        self.RT = [[] for i in range(self.nactions)]
        self.requer = [[] for i in range(self.nactions)]
        self.stop = [[] for i in range(self.nactions)]
        self.param_values = [[] for i in range(self.nactions)]
        self.values_children = [[] for i in range(self.nactions)]
        self.nvalue = []
        
        param = 1
        nval = 0
        for lin in lines[3:]:
            tmp = func.spe_split('\s(\d*\.\d*|\d+)|\s([a-zA-Z0-9_]*)',lin)
            if int(tmp[0]) == param:
                nval += 1
            else:
                param+=1
                self.nvalue.append(nval)
                nval = 1
            aux = [float(x) for x in tmp[3:len(tmp)]]
            self.param_values[int(tmp[0])-1].append(tmp[2])
            self.values_children[int(tmp[0])-1].append(int(tmp[1]))
            self.RT[int(tmp[0])-1].append(aux[0:self.ncompetences])
            self.requer[int(tmp[0])-1].append(aux[self.ncompetences:2*self.ncompetences])
            self.stop[int(tmp[0])-1].append(func.fill_data(aux[2*self.ncompetences:],self.ncompetences))
        self.nvalue.append(nval)
        reader.close()

    def RTable(self, act, lvl=None, **kwargs):
        ## from the solution and the RTable it will compute the level it will compute the progress and provide a reward to the SSB
        ## wrong assuming always right, debugging

        if lvl is None :
            lvl = [1]*self.ncompetences
        for ii in range(self.nactions):
            lvl = [a*b for a,b in zip(lvl,self.RT[ii][act[ii]])]
        
        #if "dict_form" in kwargs.keys():
        #    lvl_dict = {key: value for (key,value) in zip(self.competences,lvl)}
        #    return lvl_dict

        return lvl

    def calcul_reward(self, lvl, corsol, answer_impact):
        r_KC = [0]*self.ncompetences
        for i in range(self.ncompetences):
            diff = lvl[i]-self.estim_level[i]
            if (diff > 0 and answer_impact[i] == 1) or (diff < 0 and answer_impact[i] == 0):
                r_KC[i] = diff

        for i in range(self.ncompetences):
            self.estim_level[i] = self.estim_level[i] + self.levelupdate*r_KC[i]
        r = max(0,sum(r_KC)/self.ncompetences)
        return r

    def update(self, lvl, act, corsol, answer_impact, *args, **kwargs):
        r_KC = self.calcul_reward(lvl,corsol,answer_impact)

        for ii in range(self.nactions):
            # update the value of each bandit
            self.SSB[ii].success[act[ii]].append(np.mean(answer_impact))
            self.nbturn[ii] += 1
            self.SSB[ii].update(act[ii], r_KC)
            self.SSB[ii].promote(self.estim_level)


## class RiaritSsbg
#########################################################

#########################################################
#########################################################
## class RiaritSsb

class RiaritSsb(SSbandit):

    def __init__(self, id, nval, nKC, requer, stop, is_hierarchical=0, param_values = [], params = {}):
        # params : 

        SSbandit.__init__(self,id, nval, is_hierarchical,param_values, params=params)
        #self.name = "rssb"
        self.requer = requer
        self.stop = stop
        init_level = [0.0]*nKC
        self.promote(init_level,True)

    def promote(self, lvl, init=False):
        for ii in range(self.nval):
            if( np.array(lvl) >= np.array(self.requer[ii]) ).all() and (np.array(lvl) <= np.array(self.stop[ii])).any():
                if(self.bandval[ii]== 0 ):
                    if init == True :
                        self.bandval[ii] = self.uniformval
                    else :
                        self.bandval[ii] = max(self.bandval)

            if(np.array(lvl)>np.array(self.stop[ii]) ).all():
                if(self.bandval[ii] != 0 ):
                    self.bandval[ii] = 0

        return

## class RiaritSsb
#########################################################
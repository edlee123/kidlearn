#-*- coding: utf-8 -*-
## Right Activity at the Right Time
## 2014 BCLEMENT

from hssbg import *

# class RIARIT_ssbg(object): pass
# class RIARIT_ssb(object): pass

#########################################################
#########################################################
## class RIARIT_hssb

class RIARIT_hssbg(HierarchySSBG):

    # ssbgClasse = RIARIT_ssbg

    def __init__(self, params = None, params_file = "seq_test_1", directory = "params_files"):
        # params : RT, path

        params = params or func.load_json(params_file,directory)
        self.current_lvl_ex = {}
        
        HierarchySSBG.__init__(self, params = params)
        self.load_Error()
        #self.CreateHSSBG(RT)

        return
    def get_KC(self):
        return self.SSBGs[self.main_act].competences

    def get_state(self):
        state = HierarchySSBG.get_state(self)
        state["estim_lvl"] = self.get_estim_level(self.main_act, dict_form = 1)
        return state

    def get_estim_level(self,RT = "", *args, **kwargs):
        level = {}
        for nameRT,ssbg in self.SSBGs.items():
            level[nameRT] = ssbg.get_estim_level(**kwargs)
        if RT != "":
            return {RT : level[RT]}
        return level

    def setLevel(self,levels):
        for RT,lvl in levels.items():
            self.SSBGs[RT].setLevel(lvl)
        return

    def instantiate_ssbg(self,RT):
        params = self.params["RIARIT_ssbg"]
        params["RT"] = RT
        return RIARIT_ssbg(params = params)

    def compute_act_lvl(self, act, RT = None, **kwargs):
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

    def addSsbgToCompute(self,pre_ssbg,act,lvl = None,**kwargs):
        #if lvl == None:
        #    lvl = [1]*self.ncompetences
        #print pre_ssbg.ID
        #print act
        for actRT in range(len(pre_ssbg.using_RT)):
            nameRT = pre_ssbg.using_RT[actRT][act[pre_ssbg.ID][actRT]]
            if nameRT[0:2] != 'NO':
                self.ssbg_used.append(nameRT)
                lvl = self.addSsbgToCompute(self.SSBGs[nameRT],act,lvl, **kwargs)

        lvl = pre_ssbg.RTable(act[pre_ssbg.ID],lvl, **kwargs)
        self.current_lvl_ex[pre_ssbg.ID] = lvl
        pre_ssbg.ID

        return lvl

    def update(self, act, corsol = True, error_ID = None, *args, **kwargs):
        #if act is None:
        #    act = self.lastAct
        #self.computelvl(act)

        answer_impact = self.return_answer_impact(corsol,error_ID)

        for nameRT in act.keys():
            self.SSBGs[nameRT].update(self.current_lvl_ex[nameRT],act[nameRT], corsol, answer_impact)
        return

    def load_Error(self, RT_ID = "MAIN", directory = 'assets/algorithm/error_RT/'):
        self.error_tab = []
        self.error_ID_tab = []
        file_to_read = "%serror_%s%s" % (directory,RT_ID,".txt")
        try:
            reader = open(file_to_read, 'rb')
            lines = reader.readlines()
            for lin in lines[2:]:
                tmp=spe_split('\s(\d*\.\d*|\d+)|\s([a-zA-Z0-9_]*)',lin)
                aux = [float(x) for x in tmp[2:len(tmp)]]
                self.error_ID_tab.append(tmp[1])
                self.error_tab.append(aux[0:self.ncompetences])
        except:
            return
        return

    def return_answer_impact(self,corsol,error_ID = None):
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
## class RIARIT_ssbg
class RIARIT_ssbg(SSBanditGroup):

    def __init__(self,params = None, params_file = "Rssb_test_1", directory = "params_files"):
        SSBanditGroup.__init__(self,params = params)
        self.levelupdate = params["levelupdate"]
        
        return

    def instanciate_ssb(self,ii,is_hierarchical):
        params = self.params["RIARIT_ssb"]

        return RIARIT_ssb(ii,len(self.RT[ii]),self.ncompetences,self.requer[ii], self.stop[ii], is_hierarchical = is_hierarchical, using_RT = self.using_RT[ii], params = params)

    def get_estim_level(self,**kwargs):
        if "dict_form" in kwargs.keys():
            return {key: value for (key,value) in zip(self.competences,self.estim_level)}
        return self.estim_level

    def setLevel(self,level):
        self.estim_level = level
        return

    def calDiffLvl(self,lvl):
        lvlDiff = []
        for i in range(self.ncompetences):
            lvlDiff.append(lvl[i]-self.estim_level[i])
        return lvlDiff
        
    def loadRT(self,RT):
        path_RT = "%s/%s.txt" % (RT["path"], RT["name"])
        reader = open(path_RT, 'rb')
        self.ID = ((path_RT.split("/")[-1]).split(".")[0])
        #self.ID = ((path_RT.split("/")[-1]).split(".")[0]).split("_")[1]
        #print "SSB CREATE: %s" % self.ID
        lines = reader.readlines()
        tmp = spe_split('\W',lines[0])
        self.competences = tmp[1:len(tmp)]
        self.ncompetences = len(self.competences)   
        self.estim_level = [0]*self.ncompetences

        tmp = spe_split('\W',lines[1])
        self.actions = tmp[1:len(tmp)]
        self.nactions = len(self.actions)
        self.act = [0]*self.nactions
        self.nbturn = [0]*self.nactions

        tmp = spe_split('\W',lines[3])
        self.nb_stay = [int(x) for x in tmp[1:len(tmp)]] + [int(x)]*(self.nactions-(len(tmp)-1))

        self.RT = [[] for i in range(self.nactions)]
        self.requer = [[] for i in range(self.nactions)]
        self.stop = [[] for i in range(self.nactions)]
        self.using_RT = [[] for i in range(self.nactions)]
        self.nvalue = []
        
        param = 1
        nval = 0
        for lin in lines[4:]:
            tmp=spe_split('\s(\d*\.\d*|\d+)|\s([a-zA-Z0-9_]*)',lin)
            if int(tmp[0]) == param:
                nval += 1
            else:
                param+=1
                self.nvalue.append(nval)
                nval = 1
            aux = [float(x) for x in tmp[2:len(tmp)]]
            self.using_RT[int(tmp[0])-1].append(tmp[1])
            self.RT[int(tmp[0])-1].append(aux[0:self.ncompetences])
            self.requer[int(tmp[0])-1].append(aux[self.ncompetences:2*self.ncompetences])
            self.stop[int(tmp[0])-1].append(aux[2*self.ncompetences:])
        self.nvalue.append(nval)
        reader.close()
        self.CreateSSBs()
        #self.load_Error()

        return

    def RTable(self, act,lvl = None, **kwargs):
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

    def calcul_reward(self,lvl,corsol,answer_impact):
        r_KC = [0]*self.ncompetences
        for i in range(self.ncompetences):
            diff = lvl[i]-self.estim_level[i]
            if (diff > 0 and answer_impact[i] == 1) or (diff < 0 and answer_impact[i] == 0):
                r_KC[i] = diff

        for i in range(self.ncompetences):
            self.estim_level[i] = self.estim_level[i] + self.levelupdate*r_KC[i]
        r = max(0,sum(r_KC)/self.ncompetences)
        return r

    def update(self,lvl,act,corsol,answer_impact,*args, **kwargs):
        r_KC = self.calcul_reward(lvl,corsol,answer_impact)

        for ii in range(self.nactions):
            # update the value of each bandit
            self.SSB[ii].success[act[ii]].append(mean(answer_impact))
            self.nbturn[ii] += 1
            self.SSB[ii].update(act[ii], r_KC)
            self.SSB[ii].promote(self.estim_level)

RIARIT_hssbg.ssbgClasse = RIARIT_ssbg

## class RIARIT_ssbg
#########################################################

#########################################################
#########################################################
## class RIARIT_ssb

class RIARIT_ssb(SSbandit):

    def __init__(self,id, nval, ntask, requer, stop, is_hierarchical = 0, using_RT = [], params = {}):
        # params : 

        SSbandit.__init__(self,id, nval, ntask, is_hierarchical,using_RT, params = params)

        self.requer = requer
        self.stop = stop
        self.promote([0.0]*ntask,True)

    def promote(self,lvl,init = False):
        for ii in range(self.nval):
            if( array(lvl) >= array(self.requer[ii]) ).all() and (array(lvl) <= array(self.stop[ii])).any():
                if(self.bandval[ii]== 0 ):
                    if init == True :
                        self.bandval[ii] = self.uniformval
                    else :
                        self.bandval[ii] = max(self.bandval)

            if(array(lvl)>array(self.stop[ii]) ).all():
                if(self.bandval[ii] != 0 ):
                    self.bandval[ii] = 0

        return

## class RIARIT_ssb
#########################################################
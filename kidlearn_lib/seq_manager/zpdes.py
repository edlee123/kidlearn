#-*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        ZPDES
# Purpose:     Zone of Proximal Development and Empirical Success
#
# Author:      Bclement
#
# Created:     14-03-2015
# Copyright:   (c) BClement 2015
# Licence:     GNU Affero General Public License v3.0
#-------------------------------------------------------------------------------

import numpy as np

from .riarit import RiaritHssbg, RiaritSsbg, RiaritSsb
from .hssbg import HierarchicalSSBG, SSBanditGroup, SSbandit
from .. import functions as func

#########################################################
#########################################################
# class ZpdesHssbg


class ZpdesHssbg(HierarchicalSSBG):

    def __init__(self, params=None, params_file="seq_test_1", directory="params_files"):
        # params : RT, path

        params = params or func.load_json(params_file, directory)
        HierarchicalSSBG.__init__(self, params=params)
        self.current_lvl_ex = {}
        if "riarit" in params.keys():
            self.riarit = RiaritHssbg(params_file=params["riarit"]["file_name"], directory=params["riarit"]["path"])
        else:
            self.riarit = None
        # self.load_Error()
        # self.CreateHSSBG(RT)

        return

    def compute_act_lvl(self, act, RT=None, **kwargs):
        if self.riarit is not None:
            return self.riarit.compute_act_lvl(act, RT)
        else:
            values_worked = []
            for key, val in act.items():
                values_worked.append(str(self.SSBGs[key].SSB[0].param_values[val[0]]))

            lvl = [0] * self.ncompetencies
            for i in range(0, self.ncompetencies):
                p_name = "V{}".format(i + 1)
                if p_name in values_worked:
                    lvl[i] = 1
            return lvl

    def instantiate_ssbg(self, graph_def):
        params = self.params["ZpdesSsbg"]
        params["graph_def"] = graph_def
        return ZpdesSsbg(params=params)

    def CreateHSSBG(self, graph_infos):
        if "act_prime" in graph_infos.keys():
            graph_def = graph_infos
        else:
            graph_def = func.load_json(graph_infos["file_name"], graph_infos["path"])

        self.ncompetencies = graph_def["ncompetencies"]
        graph_def["current_ssbg"] = graph_def["act_prime"]
        mainSSBG = self.instantiate_ssbg(graph_def)
        self.SSBGs = {}
        self.SSBGs[self.main_act] = mainSSBG
        self.addSSBG(mainSSBG, graph_def)
        #self.lastAct = {}
        return

    def addSSBG(self, ssbg_father, graph_def):
        for actRT, hierarchy, i in zip(ssbg_father.param_values, ssbg_father.values_children, range(len(ssbg_father.param_values))):
            for nameRT, hierar in zip(actRT, hierarchy):
                if hierar and nameRT not in self.SSBGs.keys():
                    graph_def["current_ssbg"] = nameRT
                    #RT = "%s/%s.txt" % (self.graph_path, nameRT)
                    nssbg = self.instantiate_ssbg(graph_def)
                    self.SSBGs[nameRT] = nssbg
                    ssbg_father.add_sonSSBG(i, self.SSBGs[nameRT])
                    self.addSSBG(nssbg, graph_def)
                elif hierar:
                    ssbg_father.add_sonSSBG(i, self.SSBGs[nameRT])

    def update(self, act, result, *args):
        result_impact = self.compute_result_impact(result)

        for nameRT in act.keys():
            self.SSBGs[nameRT].update(act[nameRT], result_impact)
        return

    def compute_result_impact(self, result):
        return result

# class RiaritHssbg
#########################################################

#########################################################
#########################################################
# class ZpdesSsbg


class ZpdesSsbg(SSBanditGroup):

    def __init__(self, params=None, params_file="Rssb_test_1", directory="params_files"):
        SSBanditGroup.__init__(self, params=params)
        self.loadSsbg(self.params["graph_def"])

    def loadSsbg(self, graph_def):
        self.ID = graph_def["current_ssbg"]
        ssbg_def = graph_def[self.ID]
        #self.actions = ssbg_def[0]
        self.nactions = len(ssbg_def["ssbg"])
        self.act = [0] * self.nactions
        if "init_ssb" in ssbg_def.keys():
            self.init_ssb = ssbg_def["init_ssb"]
        else:
            self.init_ssb = [[0] for x in range(self.nactions)]

        if "h" in ssbg_def.keys():
            self.h_actions = ssbg_def["h"]
        else:
            self.h_actions = [0] * self.nactions

        if "actions" in ssbg_def.keys():
            self.actions = ssbg_def["actions"]
        else:
            self.actions = ["{}_act{}".format(self.ID, x) for x in range(self.nactions)]

        if "nb_stay" in ssbg_def.keys():
            self.nb_stay = ssbg_def["nb_stay"]
        else:
            self.nb_stay = [1] * self.nactions

        self.nbturn = [0] * self.nactions
        self.param_values = [[] for i in range(self.nactions)]
        self.values_children = [[] for i in range(self.nactions)]
        self.nvalue = []

        for act in range(self.nactions):
            self.nvalue.append(len(ssbg_def["ssbg"][act]))
            for val in ssbg_def["ssbg"][act]:
                self.values_children[act].append(int(val in graph_def.keys()))
                self.param_values[act].append(val)

        self.CreateSSBs()

    def instanciate_ssb(self, ii, is_hierarchical):
        params = self.params["ZpdesSsb"]
        params["init_ssb"] = self.init_ssb[ii]

        return ZpdesSsb(ii, self.nvalue[ii], is_hierarchical=is_hierarchical, param_values=self.param_values[ii], params=params)

    def calcul_reward(self, act, answer_impact):
        coeff_ans = answer_impact
        r_ES = []
        for ii in range(self.nactions):
            r_ES.append(self.SSB[ii].calcul_reward_ssb(act[ii], coeff_ans))
        return r_ES

    def update(self, act, result_impact, *args, **kwargs):
        r_ES = self.calcul_reward(act, result_impact)

        # For simulation
        #r_KC = RiaritSsbg.calcul_reward(self,lvl,result,answer_impact = result)
        # For simulation

        for ii in range(self.nactions):
            self.nbturn[ii] += 1
            # if len(self.SSB[ii].sonSSBG.keys()) > 0:
            #    r_ES[ii] += pow(10,-5)*all_act[self.param_values[ii][act[ii]]][0]/len(self.SSB[ii].sonSSBG[self.param_values[ii][act[ii]]].SSB[0].bandval)
                # raw_input()
            self.SSB[ii].update(act[ii], max(0, r_ES[ii]))
            self.SSB[ii].promote()

# class ZpdesSsbg
#########################################################

#########################################################
#########################################################
# class ZpdesSsb


class ZpdesSsb(SSbandit):

    def __init__(self, id, nval, is_hierarchical=0, param_values=None, params=None):
        # params :
        if param_values is None:
            param_values = []
        if params is None:
            params = {}

        SSbandit.__init__(self, id, nval, is_hierarchical, param_values, params=params)
        #self.name = "zssb"
        self.stepUpdate = params['stepUpdate']
        self.stepMax = self.stepUpdate / 2

        func.setattr_dic_or_default(self, "size_window", params, 3)
        func.setattr_dic_or_default(self, "init_ssb", params, [0])
        self.size_window = min(len(self.bandval), self.size_window)

        func.setattr_dic_or_default(self, "upZPDval", params, 0.5)
        func.setattr_dic_or_default(self, "deactZPDval", params, 0.8)

        func.setattr_dic_or_default(self, "promote_coeff", params, 1)
        func.setattr_dic_or_default(self, "h_promote_coeff", params, 1)
        func.setattr_dic_or_default(self, "thresHProm", params, 0.3)
        func.setattr_dic_or_default(self, "thresHDeact", params, 0.7)
        func.setattr_dic_or_default(self, "spe_promo", params, 0)

        self.promote(True)

    def hierarchical_promote(self):
        for i in range(1, self.nval):
            if(self.bandval[i] == 0):
                try:
                    ssbg = self.sonSSBG[self.param_values[i - 1]]
                except:
                    print "son : %s, i : %s, lenact : %s, uRT : %s" % (self.sonSSBG, i, self.nval, self.param_values)
                successUsed = []
                sumSucess = 0
                for ssb in ssbg.SSB:
                    if ssb.is_hierarchical == 1:
                        for suc in ssb.success:
                            if suc == []:
                                sucToTreat = [0]
                            else:
                                sucToTreat = suc
                            stepSuccess = min(len(sucToTreat), self.stepMax)
                            successUsed.append(sucToTreat[-stepSuccess:])

                            if len(sucToTreat[-stepSuccess:]) > 0:
                                sumSucess += np.mean(sucToTreat[-stepSuccess:])
                            else:
                                sumSucess += 0

                meanSucess = sumSucess * 1.0 / max(len(successUsed), 1)

                if meanSucess > self.thresHProm:
                    self.bandval[i] = self.bandval[i - 1] * self.h_promote_coeff  # TODO test with 4 for exemple

    def hierarchical_promote_async(self):
        for i in range(1, self.nval):
            ssbgi1 = self.sonSSBG[self.param_values[i - 1]]
            tabTabSucessRatei1 = self.hsuccess_rate(ssbgi1, -self.stepMax)
            tabMeanSucessRatei1 = [np.mean(tab) for tab in tabTabSucessRatei1]
            meanSucessi1 = np.mean(tabMeanSucessRatei1)

            ssbgi = self.sonSSBG[self.param_values[i]]
            tabTabSucessRatei = self.hsuccess_rate(ssbgi, -self.stepUpdate)
            minTabTabSucessRatei = min([min(tab) for tab in tabTabSucessRatei])

            if self.bandval[i] == 0 and self.len_success()[i] == 0 and meanSucessi1 > self.thresHProm:
                self.bandval[i] = self.bandval[i - 1] * self.h_promote_coeff
            elif self.bandval[i] != 0 and minTabTabSucessRatei > self.thresHDeact and self.bandval.count(0) < len(self.bandval) - 1:
                self.bandval[i] = 0

    def spe_promote_async(self):
        succrate_active = self.success_rate(-self.stepMax,
                                            val=self.active_bandits(),
                                            min_nb_ans=2)

        if succrate_active > self.upZPDval and 0 in self.len_success():  # and imax not in self.use_to_active: # and first < len(self.bandval) - 3:
            self.bandval[self.len_success().index(0)] = min([self.bandval[x] for x in self.active_bandits()]) * self.promote_coeff

        max_usable_val_to_deact = [self.success_rate(-self.stepUpdate, val=[x]) for x in self.active_bandits() if self.len_success()[x] >= self.stepUpdate]

        if len(max_usable_val_to_deact) > 0:
            imaxd = self.active_bandits()[np.argmax(max_usable_val_to_deact)]
            max_succrate_active_todeact = self.success_rate(-self.stepUpdate, val=[imaxd])

            if max_succrate_active_todeact > self.deactZPDval and self.bandval.count(0) < len(self.bandval) - 1:  # imaxd != self.nval-1:
                # if self.bandval.count(0) < len(self.bandval)-1:
                self.bandval[imaxd] = 0

    def spe_promote_windows(self):
        # Promote initialisation for beginning of the sequence with less than windows size bandit activated
        if self.nval - self.len_success().count(0) < self.size_window:
            i = self.len_success().index(0)
            if self.success_rate(-self.stepMax, val=[i - 1]) > self.upZPDval and len(self.success[i - 1]) > 1:
                self.bandval[i] = self.bandval[i - 1]
        else:
            first = -1
            for ii in range(self.nval):
                if self.bandval[ii] != 0:
                    first = ii
                    break
            for ii in range(self.nval):
                if self.bandval[ii] != 0:
                    last = ii

            valToUp = self.deactZPDval
            if first >= len(self.bandval) - 3:
                valToUp = self.deactZPDval

            if len(self.success[first][-self.stepMax:]) > 0:
                if np.mean(self.success[first][-self.stepMax:]) > valToUp and len(self.success[last]) >= self.stepMax and first != last:
                    self.bandval[first] = 0

                    if first + 3 < len(self.bandval):
                        self.bandval[first + 3] = min(self.bandval[first + 2], self.bandval[first + 1]) / 2

    def promote(self, init=False):
        # Promote if initialisation
        if init is True:
            for ii in self.init_ssb:
                self.bandval[ii] = self.uniformval  # /pow((ii+1),7)

        elif self.is_hierarchical:

            # Promote wicth son action
            if len(self.sonSSBG) > 0:
                self.hierarchical_promote_async()

            # Promote normal
            else:
                if self.spe_promo == 0:
                    self.spe_promote_async()
                else:
                    self.spe_promote_windows()

    def active_bandits(self):
        return [x for x in range(self.nval) if self.bandval[x] != 0]

    def not_active_bandits(self):
        return [x for x in range(self.nval) if self.bandval[x] == 0]

    def len_success(self, first_val=0, last_val=None):
        return [len(x) for x in self.success][first_val:last_val]

    def hsuccess_rate(self, ssbg, first_step=0, last_step=None, val=None, min_nb_ans=2, meanAll=0):
        successUsed = [ssb.success_rate(first_step, last_step, min_nb_ans=min_nb_ans, meanAll=meanAll) for ssb in ssbg.SSB if ssb.is_hierarchical == 1]

        return successUsed

    def success_rate(self, first_step=0, last_step=None, val=None, min_nb_ans=2, meanAll=1):
        if val is None:
            val = range(self.nval)
        elif len(val) == 0:
            return 0
        succrate = []
        for x in val:
            if len(self.success[x][first_step:last_step]) < min_nb_ans:
                succrate.append(0)
            else:
                succrate.append(np.mean(self.success[x][int(first_step):last_step]))
        #succrate = [np.mean(x[first_step:last_step]) for x in self.success][first_val:last_val]
        if len(succrate) > 1 and meanAll == 1:
            return np.mean(succrate)
        elif len(succrate) > 1:
            return succrate
        else:
            return succrate[0]

    def calcul_reward_ssb(self, val, coeff_ans):
        self.success[val].append(coeff_ans)
        # if len(self.sonSSBG.keys())> 0:
        #    print self.success
        if len(self.success[val]) > 2:
            y_step = min(self.stepUpdate, len(self.success[val]))
            y_range = y_step / 2
            sum_old = np.mean(self.success[val][-y_step:-y_range])
            sum_range = np.mean(self.success[val][-y_range:])
            r = max(0, sum_range - sum_old)
        else:
            r = self.bandval[val]

        return r


# class ZpdesSsb
#########################################################

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

from riarit import *
from hssbg import *
import numpy as np

#########################################################
#########################################################
## class ZpdesHssbg

class ZpdesHssbg(RiaritHssbg):

    #ssbgClasse = ZpdesSsbg

    def instantiate_ssbg(self,RT):
        params = self.params["ZpdesSsbg"]
        params["RT"] = RT
        return ZpdesSsbg(params = params)

    def update(self, act, corsol = True, error_ID = None, *args):
        #if act is None:
        #    act = self.lastAct
        #self.computelvl(act)
        answer_impact = self.return_answer_impact(corsol,error_ID)

        for nameRT in act.keys():
            self.SSBGs[nameRT].update(self.current_lvl_ex[nameRT],act[nameRT], corsol, answer_impact,act)
        return

## class RiaritHssbg
#########################################################

#########################################################
#########################################################
## class ZpdesSsbg
class ZpdesSsbg(RiaritSsbg):

    def instanciate_ssb(self,ii,is_hierarchical):
        params = self.params["ZpdesSsb"]

        return ZpdesSsb(ii,len(self.RT[ii]),self.ncompetences,self.requer[ii], self.stop[ii], is_hierarchical = is_hierarchical, param_values = self.param_values[ii],params = params)

    def calcul_reward(self,act,answer_impact):
        coeff_ans = mean(answer_impact)
        r_ES = []
        for ii in range(self.nactions):
            r_ES.append(self.SSB[ii].calcul_reward_ssb(act[ii],coeff_ans))
        return r_ES

    def update(self,lvl,act,corsol,answer_impact,*args, **kwargs):
        r_ES = self.calcul_reward(act,answer_impact)
        
        ## For simulation
        r_KC = RiaritSsbg.calcul_reward(self,lvl,corsol,answer_impact)
        ## For simulation

        for ii in range(self.nactions):
            self.nbturn[ii] += 1
            #if len(self.SSB[ii].sonSSBG.keys()) > 0:
            #    r_ES[ii] += pow(10,-5)*all_act[self.param_values[ii][act[ii]]][0]/len(self.SSB[ii].sonSSBG[self.param_values[ii][act[ii]]].SSB[0].bandval)
                #raw_input()
            self.SSB[ii].update(act[ii], max(0,r_ES[ii]))
            self.SSB[ii].promote()

## class ZpdesSsbg
#########################################################

#########################################################
#########################################################
## class ZpdesSsb

class ZpdesSsb(RiaritSsb):
    def __init__(self,id, nval, ntask, requer, stop,is_hierarchical = 0, param_values = [], params = {}):
        # params : 

        SSbandit.__init__(self,id, nval, ntask, is_hierarchical,param_values, params = params)
        self.name = "zssb"
        self.stepUpdate = params['stepUpdate']
        self.stepMax = self.stepUpdate/2
        self.size_window = min(len(self.bandval),params['size_window'])
        self.thresZBegin = params["thresZBegin"]
        self.upZPDval = params["upZPDval"]
        self.deactZPDval = params["deactZPDval"]
        self.thresHierarProm = params["thresHierarProm"]
        self.promote_coeff = params["promote_coeff"]
        self.hier_promote_coeff = params["h_promote_coeff"]
        if "spe_promo" in params.keys():
            self.spe_promo = params["spe_promo"]
        else:
            self.spe_promo = 0
        self.promote(True)

    def hierarchical_promote(self):
        for i in range(1,self.nval):
            if(self.bandval[i]== 0):
                try:
                    ssbg = self.sonSSBG[self.param_values[i-1]]
                except:
                    print "son : %s, i : %s, lenact : %s, uRT : %s" % (self.sonSSBG,i,self.nval,self.param_values) 
                    crash()
                successUsed = []
                sumSucess = 0
                for ssb in ssbg.SSB:
                    if ssb.is_hierarchical == 1:
                        for suc in ssb.success:
                            if suc == []:
                                sucToTreat = [0]
                            else:
                                sucToTreat = suc
                            stepSuccess = min(len(sucToTreat),self.stepMax) 
                            successUsed.append(sucToTreat[-stepSuccess:])
                            
                            if len(sucToTreat[-stepSuccess:]) > 0: 
                                sumSucess += mean(sucToTreat[-stepSuccess:])
                            else :
                                sumSucess += 0

                meanSucess = sumSucess*1.0/max(len(successUsed),1)

                if meanSucess > self.thresHierarProm:
                    self.bandval[i] = self.bandval[i-1]*self.hier_promote_coeff #TODO test with 4 for exemple

    def spe_promo_thib(self):
        stepSuccess = self.stepMax

        succrate_active = self.success_rate(-self.stepMax, val = self.active_bandits())

        if succrate_active > self.upZPDval and 0 in self.len_success():# and imax not in self.use_to_active: # and first < len(self.bandval) - 3:
              self.bandval[self.len_success().index(0)] = min([self.bandval[x] for x in self.active_bandits()])*self.promote_coeff

        max_usable_val_to_deact = [self.success_rate(-self.stepUpdate,val =[x]) for x in self.active_bandits() if self.len_success()[x] >= self.stepUpdate]
        
        if len(max_usable_val_to_deact) > 0:
            imaxd = self.active_bandits()[np.argmax(max_usable_val_to_deact)]
            max_succrate_active_todeact = self.success_rate(-self.stepUpdate, val = [imaxd])

            if max_succrate_active_todeact > self.deactZPDval and imaxd != self.nval-1:
                self.bandval[imaxd] = 0

    def spe_promo_no_wind(self):
        stepSuccess = self.stepMax
        sizeWind = self.size_window

        max_usable_val = [self.success_rate(-stepSuccess,val =[x]) for x in self.active_bandits() if self.len_success()[x] >= self.stepMax]
        min_usable_val = [self.success_rate(-stepSuccess,val = [x]) for x in self.not_active_bandits() if self.len_success()[x] >= self.stepUpdate]

        if len(max_usable_val) > 0:
            imax = self.active_bandits()[np.argmax(max_usable_val)]
            max_succrate_active = self.success_rate(-self.stepMax, val = [imax])

            if 0 in self.len_success() and max_succrate_active > self.upZPDval:
                self.bandval[self.len_success().index(0)] = min([self.bandval[x] for x in self.active_bandits()])*self.promote_coeff

            if len(self.not_active_bandits()) > 0 and max_succrate_active > 0.9 and 0 not in self.len_success():# and len(self.success[imax]) > self.stepMax:
                imin = self.not_active_bandits()[np.argmin([self.success_rate(-stepSuccess, val = self.not_active_bandits())])]
                min_succrate_not_active = self.success_rate(-self.stepUpdate,val = [imin])

                ####################################################################
                # differ => spero promo len
                if self.spe_promo == 1:
                    self.spe_promo_min_len(imax,imin,stepSuccess,min_succrate_not_active)
                #######################################################################

                elif min_succrate_not_active < 1 :
                    self.bandval[imin] = min([self.bandval[x] for x in self.active_bandits()])
                    self.bandval[imax] = 0
            
            elif max_succrate_active > self.deactZPDval and len(self.active_bandits()) >= sizeWind :
                    self.bandval[imax] = 0

    # Special Promote where we test the lengh of success
    def spe_promo_min_len(self,imax,imin,stepSuccess,min_succrate_not_active):
        ilen_min = self.not_active_bandits()[np.argmin([self.len_success()[x] for x in self.not_active_bandits()])]
        len_min = self.len_success()[ilen_min]

        if len_min < self.stepUpdate and imax != ilen_min:
            self.bandval[ilen_min] = min([self.bandval[x] for x in self.active_bandits()])
            self.bandval[imax] = 0

        elif min_succrate_not_active < 1 :
            self.bandval[imin] = min([self.bandval[x] for x in self.active_bandits()])
            self.bandval[imax] = 0


    # Special Promote with a windows activ and desactivation are not sync
    def spe_promo_window_not_sync(self):
        stepSuccess = self.stepMax

        last = self.nval-1
        for ii in range(self.nval-1,-1,-1):
            if self.bandval[ii] != 0:
                last = ii
                break

        max_usable_val = [self.success_rate(-stepSuccess,val =[x]) for x in self.active_bandits() if self.len_success()[x] >= self.stepMax and x not in self.use_to_active]

        if len(max_usable_val) > 0:
            imax = self.active_bandits()[np.argmax(max_usable_val)]
            max_succrate_active = self.success_rate(-self.stepMax, val = [imax])

            if max_succrate_active > self.upZPDval and last+1 < len(self.bandval):# and imax not in self.use_to_active: # and first < len(self.bandval) - 3:
                self.bandval[last+1] = min(self.bandval[last],self.bandval[last-1])/2
                self.use_to_active.append(imax)
                last = last+1

        max_usable_val_to_deact = [self.success_rate(-self.stepUpdate,val =[x]) for x in self.active_bandits() if self.len_success()[x] >= self.stepUpdate]
        
        if len(max_usable_val_to_deact) > 0:
            imaxd = self.active_bandits()[np.argmax(max_usable_val_to_deact)]
            max_succrate_active_todeact = self.success_rate(-self.stepUpdate, val = [imaxd])

            if max_succrate_active_todeact > self.deactZPDval and imaxd != last:
                self.bandval[imaxd] = 0

    def promote(self,init = False):

        # Promote if initialisation
        if init == True :
            self.use_to_active = []
            self.past_prom = 0
            self.past_active = []
            self.past_deactive = []

            for ii in range((1-self.is_hierarchical)*(len(self.bandval)-1)+1):
                self.bandval[ii] = self.uniformval#/pow((ii+1),7)

        elif self.is_hierarchical:
            
            #Promote wicth son action
            if len(self.sonSSBG) > 0:
                self.hierarchical_promote()

            #Promote for beginning of the sequence with less than windows size bandit activated 
            elif self.nval - self.len_success().count(0) < self.size_window :
                i = self.len_success().index(0)
                if self.success_rate(-self.stepMax,val =[i-1]) > self.thresZBegin and len(self.success[i-1]) > 1 :
                    self.bandval[i] = self.bandval[i-1]
            
            # Promote normal, when the windows moove
            else:
                if self.spe_promo < 2:
                    self.spe_promo_no_wind()
                elif self.spe_promo == 2:
                    self.spe_promo_window_not_sync()
                else:
                    self.spe_promo_thib()



    def active_bandits(self):
        return [x for x in range(self.nval) if self.bandval[x] != 0]

    def not_active_bandits(self):
        return [x for x in range(self.nval) if self.bandval[x] == 0]

    def len_success(self,first_val = 0, last_val = None):
        return [len(x) for x in self.success][first_val:last_val]

    def success_rate(self,first_step = 0,last_step = None, val = None):
        if val == None:
            val = range(self.nval)
        succrate = []
        for x in val:
            if len(self.success[x][first_step:last_step]) == 0: 
                succrate.append(0)
            else:
                succrate.append(np.mean(self.success[x][first_step:last_step]))
        #succrate = [np.mean(x[first_step:last_step]) for x in self.success][first_val:last_val]
        if len(succrate) > 1:
            return np.mean(succrate)
        else:
            return succrate[0]

    def calcul_reward_ssb(self,val,coeff_ans):
        self.success[val].append(coeff_ans)
        #if len(self.sonSSBG.keys())> 0:
        #    print self.success
        if len(self.success[val]) > 1 :
            y_step = min(self.stepUpdate,len(self.success[val]))
            y_range = y_step/2
            if self.success[val][-y_step:-y_range] > 0:
                sum_old = mean(self.success[val][-y_step:-y_range])
            else: 
                sum_old = 0

            if self.success[val][-y_range:] > 0:
                sum_range = mean(self.success[val][-y_range:])
            else:
                sum_range = 0

            r = max(0,sum_range - sum_old)

        else:
            r = 0.5

        return r


## class ZpdesSsb
#########################################################
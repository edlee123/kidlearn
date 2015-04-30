#-*- coding: utf-8 -*-

import sys as sys
import hold_data_treat as hold
reload(hold)
import numpy as np
import scipy as scipy
import scipy.stats as sstats
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.patches import Rectangle
import pylab as pylab
from my_functions import *
#from exercise.ssb import *
#from exercise.kidlearnmonnaie import *
#from ssb import *
#from kidlearnmonnaie import *
import simulation as sim
reload(sim)
from scipy.cluster.vq import vq, kmeans, whiten, kmeans2
import copy
#from kidlearnGraph import *
import kidlearnGraph as kG
reload(kG)
import xp_data_treat as xp
reload(xp)

###############################################################################
################                                       ########################
################ Gestion of kidlearn Expe treatment    ########################
################                                       ########################
###############################################################################

###############################################################################
####################### Global organisation (hold) ############################
###############################################################################

def orgaSeqSkill(data,nb_ex_min = 80):
    nb_ex = max(nb_ex_min,data[0][0]["nb_ex"])
    #print "orgaSeqSkill %s" % nb_ex
    nb_class = len(data)
    nbStudClass = len(data[0])
    RTnames  = data[0][0]["RT"]
    nbskills = len(data[0][0]["skill_simu"][0])
    nbValueParam = data[0][0]["nbValueParam"]
    allSeq = {}
    for RT in RTnames:
        allSeq[RT] = [[[] for k in range(nb_class)] for i in range(nb_ex)]
    allEstimSkills = [[[[] for k in range(nb_class)] for i in range(nb_ex+1)] for j in range(nbskills+1)]
    allSimuSkills = [[[[] for k in range(nb_class)] for i in range(nb_ex+1)] for j in range(nbskills+1)]
    oldEstimSkill = []
    oldSimuSkill = []

    nb_stud_to_print = 0
    for c in range(nb_class):
        for user in data[c]:
            nb_stud_to_print += 1

            # Orga Seq
            for i in range(len(user["seq"])):
                for RT in user["seq"][i].keys():
                    allSeq[RT][i][c].append(user["seq"][i][RT])

            esti_skill = copy.deepcopy(user["skill_estim"])
            simu_skill = copy.deepcopy(user["skill_simu"])            

            #Orga Estim Skills
            for i in range(len(user["skill_estim"])):
                #print esti_skill[i]
                esti_skill[i].append(np.mean(user["skill_estim"][i]))
                for j in range(len(user["skill_estim"][i])):
                    allEstimSkills[j][i][c].append(esti_skill[i][j])
                #allEstimSkills[-1][i][c].append(np.mean(user["skill_estim"][i]))
            # Orga Simu Skills
            for i in range(len(user["skill_simu"])):
                simu_skill[i].append(np.mean(user["skill_simu"][i]))
                for j in range(len(user["skill_simu"][i])):
                    allSimuSkills[j][i][c].append(simu_skill[i][j])
                #allEstimSkills[-1][i][c].append(np.mean(user["skill_simu"][i]))

            if len(esti_skill) < nb_ex_min:
                nb_ex_u = len(esti_skill)-1
                for i in range(nb_ex_u, nb_ex_min):
                    esti_skill.append(esti_skill[nb_ex_u])
                    simu_skill.append(simu_skill[nb_ex_u])

            oldEstimSkill.append(esti_skill)
            oldSimuSkill.append(simu_skill)
    print nb_stud_to_print

    return [allSeq,[oldEstimSkill,oldSimuSkill],allEstimSkills,allSimuSkills,nbValueParam]

def treatSeqs(allSeq, nbValueParam):

    seqsTreatTime = {}
    speSeqsTreatTime = {}
    for RT in allSeq.keys():
        if RT not in ["CS","OS"]:#"M","R","MM","RM",
            seqsTreatTime[RT] = treatSeqsRT(allSeq[RT],allSeq["CS"],nbValueParam[RT])

    type_ex_tab = ["M","R","MM","RM"]
    nbStudClass = max([len(allSeq["MAIN"][0][x]) for x in range(len(allSeq["MAIN"][0]))])

    for RT in type_ex_tab:
        speSeqsTreatTime[RT] = treatSpeSeqsRT(allSeq[RT],allSeq["CS"],nbValueParam[RT],allSeq["MAIN"],nbValueParam["MAIN"],type_ex_tab,RT,nbStudClass)

    return [seqsTreatTime,speSeqsTreatTime]

def treatSpeSeqsRT(seqData,Answers,nbValueParam,seqMain,nbParaMAIN,type_ex_tab,RT,nbStudClass,nb_ex_min = 80):
    #while [] in seqData:
     #   seqData.remove([])
    nb_ex = max(nb_ex_min,len(seqData))
    #print "treatSpeSeqsRT %s" % nb_ex

    nb_class = len(seqData[0])
    nb_param = len(nbValueParam)
    nbStudClass = nbStudClass
    speSeqTime = [[[] for j in range(nb_class)] for i in range(nb_param)]
    indiceRT = type_ex_tab.index(RT)
    spe_type_ex_tab = copy.deepcopy(type_ex_tab)
    spe_type_ex_tab.remove(RT)

    for k in range(nb_param):
        for i in range(nb_ex):
            for j in range(nb_class):
                speSeqTime[k][j].append([0]*(nbValueParam[k]+nbParaMAIN[0]-1))

    for k in range(nb_param):
        for i in range(nb_ex):
            for j in range(nb_class):
                speS = 0
                #nbStudClass = len(seqData[i][j])
                for s in range(nbStudClass):#len(seqData[i][j])):
                    #print "i : %s,j: %s ,s : %s" % (i,j,s)
                    #print "seqMain %s, i : %s, j : %s, s : %s" % (len(seqMain),len(seqMain[i]),len(seqMain[i][j]),len(seqMain[i][j][s]))
                    if s < len(seqMain[i][j]): 
                        if seqMain[i][j][s][0] == indiceRT:
                            speSeqTime[k][j][i][seqData[i][j][speS][k]] += 1
                            speS += 1
                        else:
                            tempRT = type_ex_tab[seqMain[i][j][s][0]]
                            indTempRT = nbValueParam[k] + spe_type_ex_tab.index(tempRT)
                            speSeqTime[k][j][i][indTempRT] += 1

    return speSeqTime


def treatSeqsRT(seqData,Answers,nbValueParam,nb_ex_min = 80):
    nb_ex = max(nb_ex_min,len(seqData))
    #print "treatSeqsRT %s" % nb_ex
    nb_class = len(seqData[0])
    nb_param = len(nbValueParam)
    seqTime = [[[] for j in range(nb_class)] for i in range(nb_param)]

    for k in range(nb_param):
        for i in range(nb_ex):
            for j in range(nb_class):
                seqTime[k][j].append([0]*nbValueParam[k])

    for k in range(nb_param):
        for i in range(nb_ex):
            for j in range(nb_class):
                for s in range(len(seqData[i][j])):
                    seqTime[k][j][i][seqData[i][j][s][k]] += 1

    return seqTime

def treatErrors(seqErrors,nb_ex_min = 80, jump_error = 2):
    nb_ex =  max(nb_ex_min,len(seqErrors))
    #print "treatErrors %s" % nb_ex
    nb_class =  len(seqErrors[0])
    #nbStudClass = len(seqErrors[0][0])
    errors_cumul = [[] for i in range(nb_ex)]
    studErrors = [[] for x in range(nb_class)] # [[0]*nbStudClass]*nb_class
    for i in range(nb_ex):
        for j in range(nb_class):
            nbStudClass = len(seqErrors[i][j])
            if len(studErrors[j]) < nbStudClass:
                for nbstud in range(nbStudClass - len(studErrors[j])):
                    studErrors[j].append(0)
            for k in range(nbStudClass):
                studErrors[j][k] += 1- seqErrors[i][j][k]
            errors_cumul[i].append(copy.deepcopy(studErrors[j]))

    #print errors_cumul

    error_time = [[],[],[]]

    for i in range(nb_ex):
        error_time[0].append(0)
        error_time[1].append([0,0,0,0,0,0])
        error_time[2].append([0,0,0,0,0,0,0,0,0,0])

    #nbStudClass = len(seqErrors[0][0])
    many_ex  = 0
    if nb_ex > 100:
        jump_error = 10
    for i in range(nb_ex):
        for j in range(nb_class):
            nbStudClass = len(seqErrors[i][j])
            for k in range(nbStudClass):
                for l in range(0,10):
                    #if many_ex :
                    if  errors_cumul[i][j][k] <= (l+1)*jump_error and errors_cumul[i][j][k] > (l)*jump_error: 
                        error_time[2][i][l] += 1
                        break
                    elif errors_cumul[i][j][k] > jump_error*10:
                        error_time[2][i][9] += 1
                        break
                    #else :
                     #   if  errors_cumul[i][j][k]  == l+1: 
                      #      error_time[2][i][l] += 1
                       #     break
                        #elif e[i]> 50:
                       # elif errors_cumul[i][j][k] > 10:
                        #    error_time[2][i][9] += 1
                         #   break

    return [errors_cumul,error_time]

def orgaSuccess(data,windows = [5,10,20],nb_ex_min = 80):#7,8,10]):
    nb_ex = max(nb_ex_min,data[0][0]["nb_ex"])
    #print "orgaSuccess %s" % nb_ex
    
    windows.append(nb_ex+1)
    nb_class = len(data)
    nbStudClass = len(data[0])
    RTnames  = data[0][0]["RT"]
    nbskills = len(data[0][0]["skill_simu"][0])
    nbValueParam = data[0][0]["nbValueParam"]

    allSuccess = {}
    meanSuccessWindows = []
    meanSuccess = {}
    windowSuccess = {}
    windows = [5]
    for i in range(len(windows)):
        meanSuccessWindows.append({})

    for RT in RTnames[:-2]:
        nbParam = len(nbValueParam[RT])
        allSuccess[RT] = []
        for nw in range(len(windows)):
            meanSuccessWindows[nw][RT] = []

        for nbVal in nbValueParam[RT]:
            allSuccess[RT].append([[[[] for i in range(nb_ex + 1)] for c in range(nb_class)] for n in range(nbVal)])
            #allSuccess[RT].append([[[[] for i in range(nb_ex + 1)] for c in range(nb_class)] for n in range(nbVal)])

            for nw in range(len(windows)):
                meanSuccessWindows[nw][RT].append([[[[] for i in range(nb_ex + 1)] for c in range(nb_class)] for nw in range(nbVal)])

    for c in range(nb_class):
        for user in data[c]:

            # Orga Success
            for nbex in range(nb_ex+1): #len(user["success_rate"])):
                nbexToUse = nbex
                if nbexToUse >= len(user["success_rate"]):
                    nbexToUse = len(user["success_rate"])-1
                    #print user["seq"][nbexToUse]
                for RT in user["success_rate"][nbexToUse].keys():
                    for nparam in range(len(user["success_rate"][nbexToUse][RT])):
                        for nval in range(len(user["success_rate"][nbexToUse][RT][nparam])):
                            succ = user["success_rate"][nbexToUse][RT][nparam][nval]
                            #if succ == []:
                            #    succ = []
                            #print "%s : %s" % (nparam,len(allSuccess[RT]))
                            #print "%s : %s" % (nval,len(allSuccess[RT][nparam]))
                            #print "%s : %s" % (c,len(allSuccess[RT][nparam][nval]))
                            #print "%s : %s" % (nbexToUse,len(allSuccess[RT][nparam][nval][c]))
                            #print RT 
                            #print nbex

                            if RT == "M" and RT == "MM" and 1 == 0:#and nval == 0:
                                print "ex : %s %s nparam : %s nval : %s" % (nbexToUse, RT, nparam, nval)
                                print succ

                                #raw_input()

                            allSuccess[RT][nparam][nval][c][nbex].append(succ)

                            for nw in range(len(windows)):
                                if succ == []:
                                    succ = [0]
                                win = min(windows[nw],len(succ))
                                meanSuccessWindows[nw][RT][nparam][nval][c][nbex].append(round(np.mean(succ[-win:]),4))



    return [meanSuccessWindows,allSuccess]

def treatSuccess(orgaSucc):
    allSuc = orgaSucc[1]

    allMean = []
    for typeMean in range(len(orgaSucc[0])):
        allMean.append({})
        for RT in orgaSucc[0][typeMean].keys():
            allMean[typeMean][RT]= []

            for i in range(len(orgaSucc[0][typeMean][RT])): # nparam for RT
                allMean[typeMean][RT].append([])
                for j in range(len(orgaSucc[0][typeMean][RT][i])): # nval fo iparam
                    allMean[typeMean][RT][i].append([])
                    for k in range(len(orgaSucc[0][typeMean][RT][i][j])): # class
                        allMean[typeMean][RT][i][j].append([])
                        for l in range(len(orgaSucc[0][typeMean][RT][i][j][k])): # exercise (time)
                            #print "wind : %s %s nparam : %s nval : %s, c : %s, nbex : %s" % (str(typeMean), RT,i, j, k, l)
                            #print(orgaSucc[0][typeMean][RT][i][j][k][l])
                            #print np.mean(orgaSucc[0][typeMean][RT][i][j][k][l])

                            meanToUse = np.mean(orgaSucc[0][typeMean][RT][i][j][k][l])
                            #print meanToUse
                            if orgaSucc[0][typeMean][RT][i][j][k][l] == []:
                                 meanToUse = 0

                            allMean[typeMean][RT][i][j][k].append(meanToUse)
                            #else:
                               # meanToUse = 0
                            #print meanToUse
                            #raw_input()

    #print allMean
    return allMean

###############################################################################
####################### Sucess Rate From Same Beginning #######################
###############################################################################

def findMaxSize(data):
    maxSize = max([len(data[i]) for i in range(len(data))])
    return maxSize

def egalize_Sizetab(data,maxSize = 0):
    while len(data) < maxSize:
            data.append(data[-1])
    return data

def orga_StudSucessBeginning(stud):
    studSucessBeginning = {}
    for RT,val in stud.items():
            if RT not in studSucessBeginning.keys():
                studSucessBeginning[RT] = [[] for i in range(len(val[0]))]
            for i in range(0,len(val[0])):
                for j in range(1,len(val[0][i])):
                    #studSucessBeginning[RT][i].append(np.mean(val[0][i][max(0,j-5):j]))
                    studSucessBeginning[RT][i].append(np.mean(val[0][i][max(0,j-5):j]))
    return studSucessBeginning

def orga_GroupSucessBeginning(group):
    groupSucessBeginning = {}
    meanGroupSucessBeginning = {}
    for stud in group[0]:
        studSucessBeginning = orga_StudSucessBeginning(stud["success_rate"][-1])
        for RT,val in studSucessBeginning.items():
            if RT not in groupSucessBeginning.keys():
                groupSucessBeginning[RT] = [[] for i in range(len(val))]
                meanGroupSucessBeginning[RT] = [[] for i in range(len(val))]
            for i in range(len(val)):
                if val[i] != []:# and np.mean(val[i]) < 1:
                    groupSucessBeginning[RT][i].append(val[i])

    tabRTmaxSize = {}
    for RT,val in groupSucessBeginning.items():
        for i in range(len(val)):
            if val[i] != [] : 
                nbMaxEx = max([len(val[i][x]) for x in range(len(val[i]))])
                for j in range(nbMaxEx):
                    meanGroupSucessBeginning[RT][i].append(np.mean([val[i][x][min(len(val[i][x])-1,j)] for x in range(len(val[i]))]))
            else:
                meanGroupSucessBeginning[RT][i].append(0)

        tabRTmaxSize[RT] = findMaxSize(meanGroupSucessBeginning[RT])

    for RT,val in meanGroupSucessBeginning.items():
        for i in range(len(val)):
            meanGroupSucessBeginning[RT][i] = egalize_Sizetab(meanGroupSucessBeginning[RT][i],tabRTmaxSize[RT])

    return meanGroupSucessBeginning

def orga_AllSuccessBeginning():
    all_data = recupData("result_xp/data_xp.txt","result_xp")
    datas = all_data["Datas"]
    allSuccessBeginning = []

    for group in datas :
       allSuccessBeginning.append(orga_GroupSucessBeginning(group))

    tabRTmaxSize = {}
    for RT in allSuccessBeginning[0].keys():
        tabRTmaxSize[RT] = findMaxSize([allSuccessBeginning[i][RT][0] for i in range(len(allSuccessBeginning))])
    
    finalSuccessBeg = {}
    for i in range(len(allSuccessBeginning)):
        for RT in allSuccessBeginning[i].keys():
            if RT not in finalSuccessBeg.keys():
                finalSuccessBeg[RT] = [[] for j in range(len(allSuccessBeginning[i]))]
            for j in range(len(allSuccessBeginning[i][RT])):
                finalSuccessBeg[RT][i].append(egalize_Sizetab(allSuccessBeginning[i][RT][j],tabRTmaxSize[RT]))
                #allSuccessBeginning[i][RT][j] = egalize_Sizetab(allSuccessBeginning[i][RT][j],tabRTmaxSize[RT])

    return finalSuccessBeg

def draw_AllSuccessBeginning(allSuccessBeginning):
    path = "result_xp/successbeg/"
    for RT in ["M","R","MM","RM"]:
        kG.draw_curve(allSuccessBeginning[RT],path = path, labels = [["Predefined"], ["ZPDES"], ["RiARiT"]], colors = [["#00BBBB","#00BBBB","#00BBBB","#00BBBB","#0077BB","#0077BB"],["black","black","black","black","#555555","#555555"],['#FF0000','#FF0000','#FF0000','#FF0000','#DD2222','#DD2222']], typeData = "success rate", type_data_spe = "%s" % (RT), ref = "succes_beg_all")
        
        kG.draw_curve([allSuccessBeginning[RT][0]], path = path, labels = [["Predefined"]], colors = [["black","blue","red","#99FF00","#66ccFF","#0055ff"]], typeData = "success rate", type_data_spe = "%s" % (RT), ref = "succes_beg_predef", line_type = ['solid'])

        kG.draw_curve([allSuccessBeginning[RT][1]], path = path, labels = [["ZPDES"]], colors = [["black","blue","red","#99FF00","#66ccFF","#0055ff"]], typeData = "success rate", type_data_spe = "%s" % (RT), ref = "succes_beg_zpdes", line_type = ['solid'])

        kG.draw_curve([allSuccessBeginning[RT][2]], path = path, labels = [["RiaRiT"]], colors = [["black","blue","red","#99FF00","#66ccFF","#0055ff"]], typeData = "success rate", type_data_spe = "%s" % (RT), ref = "succes_beg_riarit", line_type = ['solid'])
    return


###############################################################################
######################### Find max level reach ################################
###############################################################################

# Find RT val max level reach before alpha success rate

def findNumExLvlReach(seqCS):
    numExLvlReach = 0
    #print seqCS
    for i in range(0,len(seqCS)):
        if np.mean(seqCS[i-min(5,i):i]) < 0.8:
            numExLvlReach = i+1
            i = len(seqCS)+1 

    #raw_input()
    return numExLvlReach

def findRTValMaxLevel():
    all_data = recupData("result_xp/data_xp.txt","result_xp")
    datas = all_data["Datas"]
    RTnames = ["M","R","MM","RM"]
    csData = []
    for data in datas:
        csDataGroup = [[0]*8,[0]*6,[0]*6,[0]*6]
        for clas in data:
            for stud in clas:
                #numEx = []
                numEx = [[],[],[],[]]
                typeEx = [0,0,0,0]
                csDatastud = [[],[],[],[]] # M,R,MM,RM
                reachNotFail = [0,0,0,0]
                for j in range(len(stud["seq"])):
                    csDatastud[stud["seq"][j]["MAIN"][0]].append(stud["seq"][j]["CS"])
                    if reachNotFail[stud["seq"][j]["MAIN"][0]] == 0:
                        reachNotFail[stud["seq"][j]["MAIN"][0]] = 1
                    
                    if np.mean(csDatastud[stud["seq"][j]["MAIN"][0]][-min(len(csDatastud[stud["seq"][j]["MAIN"][0]]),10):]) < 0.8 and len(csDatastud[stud["seq"][j]["MAIN"][0]]) > 1:
                        
                        numEx[stud["seq"][j]["MAIN"][0]].append(j)
                        reachNotFail[stud["seq"][j]["MAIN"][0]] = 2
                        
                        if typeEx[stud["seq"][j]["MAIN"][0]] == 0:
                            typeEx[stud["seq"][j]["MAIN"][0]] = stud["seq"][j][RTnames[stud["seq"][j]["MAIN"][0]]][0]+1

                for i in range(len(typeEx)):
                    if reachNotFail[i] == 1:
                        csDataGroup[i][-1] += 1
                    else:
                        csDataGroup[i][typeEx[i]] += 1

                """
                for i in range(len(csDatastud)):
                    if len(csDatastud[i]) > 0:
                        numEx.append(findNumExLvlReach(csDatastud[i]))
                    else: 
                        numEx.append(0)
                if numEx != 0:
                    csDataGroup.append(numEx)
                #"""
        csData.append(csDataGroup)
    return csData

###############################################################################
# Find nb ex for each RT val

def orga_StudSuccessToFind(studSucc):
    studSuccTreated = {}
    for nbEx in range(len(studSucc)):
        for RT,val in studSucc[nbEx].items():
            if RT not in studSuccTreated.keys():
                studSuccTreated[RT] = [[] for i in range(len(val[0]))]
            for j in range(len(val[0])):
                if len(studSuccTreated[RT][j]) == 0 :
                    studSuccTreated[RT][j].append(val[0][j])
                elif len(val[0][j]) != len(studSuccTreated[RT][j][-1]):
                    studSuccTreated[RT][j].append(val[0][j])

    return studSuccTreated

def treat_StudSuccessToFind(studSuccTreated,RT = "MAIN"):
    numExLvlReach = []
    for i in range(len(studSuccTreated[RT])):
        for nbEx in range(len(studSuccTreated[RT][i])):
            if len(studSuccTreated[RT][i][nbEx]) != 0:
                if len(studSuccTreated[RT][i][nbEx]) > 2 and np.mean(studSuccTreated[RT][i][nbEx][-min(10,len(studSuccTreated[RT][i][nbEx])):-1]) < 0.8:
                    numExLvlReach.append(len(studSuccTreated[RT][i][nbEx]))
                    break
                elif nbEx == len(studSuccTreated[RT][i]) - 1:
                    #if np.mean(studSuccTreated[RT][i][nbEx][-min(10,len(studSuccTreated[RT][i][nbEx])):-1]) < 0.8:
                    numExLvlReach.append(0)#len(studSuccTreated[RT][i][nbEx]))
                    #else:
                     #   numExLvlReach.append(0)

            elif nbEx == len(studSuccTreated[RT][i]) - 1:
                numExLvlReach.append(-1)

    return numExLvlReach

def treat_findNumExLvlReach():
    all_data = recupData("result_xp/data_xp.txt","result_xp")
    datas = all_data["Datas"]
    dataNumExReach = [[[] for i in range(0,4)] for j in range(3)]

    for nbGroup in range(len(datas)):
        csDataGroup = []
        for clas in datas[nbGroup]:
            for stud in clas:
                succTreat = treat_StudSuccessToFind(orga_StudSuccessToFind(stud["success_rate"]))
                for i in range(len(succTreat)):
                    if succTreat[i] > 0:
                        dataNumExReach[nbGroup][i].append(succTreat[i])

    return dataNumExReach

    """
    for data in datas:
        dataNumExReach = [[],[],[],[]]
        meanSuccessGroup, allSuccessGroup = orgaSuccess(data)
        mainMeanSucc = meanSuccessGroup[0]["MAIN"][0]
        newMainMeanSucc = [[[] for j in range(len(mainMeanSucc[i][0][0])) ] for i in range(len(mainMeanSucc))]
        for i in range(len(mainMeanSucc)):
            for j in range(0,len(mainMeanSucc[i][0])):
                for k in range(len(mainMeanSucc[i][0][j])):
                    newMainMeanSucc[i][k].append(mainMeanSucc[i][0][j][k])

        for i in range(len(newMainMeanSucc)):
            for j in range(0,len(newMainMeanSucc[i])):
                startDoingEx = 0
                for k in range(3,len(newMainMeanSucc[i][j])):
                    if newMainMeanSucc[i][j][k] < 0.7 and newMainMeanSucc[i][j][k-1] > 0:
                        dataNumExReach[i].append(k)
                        break
                    elif k ==  len(newMainMeanSucc[i][j])-1:
                        a = 0
                        #dataNumExReach[i].append(newMainMeanSucc[i][j].index(newMainMeanSucc[i][j][k]))


        allSucess.append(dataNumExReach)
    #"""

###############################################################################
######################### Reach and achieve level #############################
###############################################################################

# Compute special group of RA lvl

def compute_groupLvlRAspeRT(data):
    groupLvlRAspeRT = []
    for i in range(len(data)):
        for x in range(int(data[i])):
            groupLvlRAspeRT.append(i)
    return groupLvlRAspeRT

def compute_allLvlRAspeRT(data):
    allLvlspeRT = []
    for group in data:
        allLvlspeRT.append(compute_groupLvlRAspeRT(group))
    return allLvlspeRT

def compute_RTLvlRA(data):
    lvlRT_RA = {}
    for key,val in data.items():
        lvlRT_RA[key] = compute_allLvlRAspeRT(val)
    return lvlRT_RA

###############################################################################
# Some other RA methods

def calcul_MeanLevelExLvl(exLvl):
    mean = 0
    for i in range(len(exLvl)):
        mean += i*exLvl[i]
    mean = 1.0*mean/sum(exLvl)
    return mean

def calcul_MeanLevelRA(exRA,ra = 0, RT = "M",algos = 0):
    return calcul_MeanLevelExEval(exRA[ra][RT][algos])

def chi2_RA(exRA,ra = 0, RT = "M",algos = [0,1], i = 0,j = 7):
    chi2Value = sstats.chi2_contingency([exRA[ra][RT][x][i:j] for x in algos])
    return chi2Value

###############################################################################

def compute_ExAchievedReachStud(seq):
    reachEx = {"M": 0, "R": 0, "MM": 0, "RM": 0}
    successEx = {"M": 0, "R": 0, "MM": 0, "RM": 0}
    for ex in seq:
        for key in reachEx.keys():
            if key in ex.keys():
                reachEx[key] = max(reachEx[key],ex[key][0]+1)
                if ex["CS"] == 1:
                    successEx[key] = max(successEx[key],ex[key][0]+1)

    return reachEx,successEx

def compute_ExAchievedReachGroup(group,cummulReachAchi = True, pourcent = False):
    #reachExGroup = {"M": [0,0,0,0,0], "R": [0,0,0,0,0], "MM": [0,0,0,0,0], "RM": [0,0,0,0,0]}
    reachExGroup = {"M": [0,0,0,0,0,0,0], "R": [0,0,0,0,0,0,0], "MM": [0,0,0,0,0,0,0], "RM": [0,0,0,0,0,0,0]}
    #achievExGroup = {"M": [0,0,0,0,0], "R": [0,0,0,0,0], "MM": [0,0,0,0,0], "RM": [0,0,0,0,0]}
    achievExGroup = {"M": [0,0,0,0,0,0,0], "R": [0,0,0,0,0,0,0], "MM": [0,0,0,0,0,0,0], "RM": [0,0,0,0,0,0,0]}
    mConvert = [0,1,2,3,4,5,6]
    #mConvert = [0,1,2,2,3,3,4]
    diffExGroup = {}
    nb_stud = 0
    for clas in group:
        for stud in clas:
            nb_stud += 1
            reach,succ = compute_ExAchievedReachStud(stud["seq"])
            for key in reach.keys():
                #if key == "M":
                 #   reach[key] = mConvert[reach[key]]
                  #  succ[key] = mConvert[succ[key]]
                if cummulReachAchi == False:
                    reachExGroup[key][reach[key]] += 1
                    achievExGroup[key][succ[key]] += 1
                else:
                    for i in range(reach[key]+1):
                        reachExGroup[key][i] += 1
                    for i in range(succ[key]+1):
                        achievExGroup[key][i] += 1
    #print nb_stud
    reachAll = []
    achieveAll = []
    for key in reachExGroup.keys():
        reachAll += reachExGroup[key]
        achieveAll += achievExGroup[key]
        #if cummulReachAchi:
         #   reachExGroup[key] = list(np.around(1.0*np.array(reachExGroup[key])/sum(reachExGroup[key])*100,1))
          #  achievExGroup[key] = list(np.around(1.0*np.array(achievExGroup[key])/sum(achievExGroup[key])*100,1))
        #else:
        if pourcent:
            reachExGroup[key] = list(np.around((1.0*np.array(reachExGroup[key])) / nb_stud*100,0))
            if sum(reachExGroup[key]) > 100:
                reachExGroup[key][2] -= (sum(reachExGroup[key]) - 100)
            achievExGroup[key] = list(np.around((1.0*np.array(achievExGroup[key])) / nb_stud*100,0))
            if sum(achievExGroup[key]) > 100:
                achievExGroup[key][2] -= (sum(achievExGroup[key]) - 100)
        diffExGroup[key] = list(np.array(reachExGroup[key]) - np.array(achievExGroup[key]))
    for i in range(len(reachAll)):
        if reachAll[i] == 0:
            reachAll[i] = 5
    reachExGroup["all"] = reachAll
    achievExGroup["all"] = achieveAll

    return reachExGroup,achievExGroup #,diffExGroup

def compute_ExAchievedReachAll(cummulReachAchi = False):
    all_data = recupData("result_xp/data_xp.txt","result_xp")
    datas = all_data["Datas"]
    allReachSuccessEx = []
    allReachExDic = {}
    allAchievExDic = {}
    for group in datas:
        reachExGroup,achievExGroup = compute_ExAchievedReachGroup(group,cummulReachAchi)
        allReachSuccessEx.append([reachExGroup,achievExGroup])
        for key in reachExGroup.keys():
            if key not in allReachExDic.keys():
                allReachExDic[key] = []
                allAchievExDic[key] = []
            allReachExDic[key].append(reachExGroup[key])
            allAchievExDic[key].append(achievExGroup[key])

    return [allReachExDic,allAchievExDic]

##################################################################
# Give just if student succeed one of RT level exercices

def sumRTlevel(cummulReachAchi = False):
    all_data = recupData("result_xp/data_xp.txt","result_xp")
    datas = all_data["Datas"]
    allSumReachExDic = []
    allSumAchievExDic = []
    for group in datas:
        reachExGroup,achievExGroup = compute_ExAchievedReachGroup(group,cummulReachAchi)
        sumReachGroup = []
        sumAchievGroup = []
        RTnames = ["M","R","MM","RM"]
        for i in range(len(RTnames)):
            #print sum(reachExGroup[RTnames[i]])
            sumReachGroup.append((1.0*sum(reachExGroup[RTnames[i]])-reachExGroup[RTnames[i]][0]))#/sum(reachExGroup[RTnames[i]])*100)
            sumAchievGroup.append(1.0*(sum(achievExGroup[RTnames[i]])-achievExGroup[RTnames[i]][0]))#/sum(reachExGroup[RTnames[i]])*100)
        allSumReachExDic.append(sumReachGroup)
        allSumAchievExDic.append(sumAchievGroup)

    return [allSumReachExDic,allSumAchievExDic]

################################################################
# Stack result

def stackedRA(cummulReachAchi = False, path = "result_xp/data_xp.txt", directory = "result_xp"):
    all_data = recupData(path,directory)
    datas = all_data["Datas"]
    allStackedReachExDic = [[],[],[],[],[],[]]
    allStackedAchievExDic = [[],[],[],[],[],[]]
    RTnames = ["M","R","MM","RM"]
    for group in datas:
        reachExGroup,achievExGroup = compute_ExAchievedReachGroup(group,cummulReachAchi)
        #for i in range(1,4):
        #    for j in range(2):
        #        reachExGroup[RTnames[i]].append(0)
        #        achievExGroup[RTnames[i]].append(0)

        stackedReachGroup = [[],[],[],[],[],[]]
        stackedAchievGroup = [[],[],[],[],[],[]]
        for i in range(len(RTnames)):
            #print sum(reachExGroup[RTnames[i]])
            for j in range(len(stackedReachGroup)):
                stackedReachGroup[j].append(reachExGroup[RTnames[i]][j+1])
                stackedAchievGroup[j].append(achievExGroup[RTnames[i]][j+1])

        for j in range(len(allStackedReachExDic)):
            allStackedReachExDic[j].append(stackedReachGroup[j])
            allStackedAchievExDic[j].append(stackedAchievGroup[j])

    return [allStackedReachExDic,allStackedAchievExDic]

#########################################################################
# Plot method

def plot_ReachAchievedEx(allReachAchievedEx,refbase = "histoRS",dataToUseRange = [0,1], plotBegin = 0, legend = ["ExpSeq","ZPDES","RiARiT","Reached","Achieved"], titlebase =  'level reached and achieved', ylab = "% of student"):
    for RT in allReachAchievedEx[0]:
        dataToPlot = [[allReachAchievedEx[x][RT][y][plotBegin:] for y in range(len(allReachAchievedEx[x][RT]))] for x in range(len(allReachAchievedEx))]
        #dataToPlot = [allReachAchievedEx[x][RT] for x in range(len(allReachAchievedEx))]
        refRT = "%s_%s" % (refbase,RT)
        title = '"%s" %s' % (RT,titlebase)
        kG.plotHisto_errorBar(dataToPlot,dataToUseRange, title = title, ref = refRT, ylab = ylab, xticks = ["Not","1","2","3","4","5","6"],hatch_tab = [None,"\\", "//"], legend = legend)

    return

###############################################################################
######################## Transition Treatment #################################
###############################################################################

# Treat all possible transition with all exercises
def treatSeqTrans(data): #data : issue to recupDtata()["Datas"]
    transitionTabs = []
    for c in range(len(data)):
        for user in data[c]:
            transitionTabs.append(user["transition_rate"])
    return transitionTabs

def clust_trans_data(data): #data : issue to recupDtata()["Datas"]
    transData = []
    all_stud = []
    for clas in data:
        for stud in clas:
            all_stud.append(stud)
            transData.append(stud["transition_rate"][0])

    print len(transData)
    print len(transData[0])
    for i in range(1,len(transData)):
        if len(transData[i]) != len(transData[i-1]):
            print len(transData[i])

    cent,clust = xp.clust_kmeans(transData,4,8,10)
    newData = [[] for x in range(len(cent))]
    
    for i in range(len(all_stud)):
        newData[clust[i]].append(all_stud[i])

    return newData

###############################################################################

# main transition organisation function only considering type and level of exercises

def orgaMainLevelTypeExTransitionAlg(data,levelTypeExTransitionAlg = {}):
    for user in data:
        userTrans = user["transExTypeLevel"]
        for typeEx1,typeEx2Tab in userTrans.items():
            if typeEx1 not in levelTypeExTransitionAlg.keys():
                levelTypeExTransitionAlg[typeEx1] = {}
            for typeEx2,nbEx in typeEx2Tab.items():
                if typeEx2 not in levelTypeExTransitionAlg[typeEx1].keys():
                    levelTypeExTransitionAlg[typeEx1][typeEx2] = 0
                levelTypeExTransitionAlg[typeEx1][typeEx2] += nbEx

    #for typeEx1 in levelTypeExTransitionAlg.keys():
     #   totTypeEx1 = 0
      #  for typeEx2,nbEx in levelTypeExTransitionAlg[typeEx1].items():
       #     totTypeEx1 += nbEx
        #for typeEx2,nbEx in levelTypeExTransitionAlg[typeEx1].items():
         #   levelTypeExTransitionAlg[typeEx1][typeEx2] = int(1.0*nbEx/totTypeEx1*500)

    return levelTypeExTransitionAlg

###############################################################################
# Orga transition only considering type and level of exercises

def orgaGroupLevelTypeExTransitionAlg(data): #data : issue to recupDtata()["Datas"]
    levelTypeExTransitionAlg = {}
    for c in range(len(data)):
        levelTypeExTransitionAlg = orgaMainLevelTypeExTransitionAlg(data[c],levelTypeExTransitionAlg)

    return levelTypeExTransitionAlg

###############################################################################
# Orga cluster of transition only considering type and level of exercises

def orgaClustLevelTypeExTransitionAlg(data): #data : issue to recupDtata()["Datas"]
    clustLevelTypeExTransitionAlg = []
    for c in range(len(data)):
        clustLevelTypeExTransitionAlg.append(orgaMainLevelTypeExTransitionAlg(data[c]))
#        levelTypeExTransitionAlg = {}
#        for user in data[c]:
#            userTrans = user["transExTypeLevel"]
#            for typeEx1,typeEx2Tab in userTrans.items():
#                if typeEx1 not in levelTypeExTransitionAlg.keys():
#                    levelTypeExTransitionAlg[typeEx1] = {}
#                for typeEx2,nbEx in typeEx2Tab.items():
#                    if typeEx2 not in levelTypeExTransitionAlg[typeEx1].keys():
#                        levelTypeExTransitionAlg[typeEx1][typeEx2] = 0
#                    levelTypeExTransitionAlg[typeEx1][typeEx2] += nbEx

    return clustLevelTypeExTransitionAlg

###############################################################################
# Orga transition along TIME only considering type and level of exercises

def orgaLevelTypeExTransitionTimeAlg(data): #data : issue to recupDtata()["Datas"]
    timeLevelTypeExTransitionAlg = {}
    for c in range(len(data)):
        for user in data[c]:
            userTrans = user["transExTypeLevelTime"]
            for typeEx1,typeEx2Tab in userTrans.items():
                if typeEx1 not in timeLevelTypeExTransitionAlg.keys():
                    timeLevelTypeExTransitionAlg[typeEx1] = {}
                for typeEx2,studEx in typeEx2Tab.items():
                    if typeEx2 not in timeLevelTypeExTransitionAlg[typeEx1].keys():
                        #timeLevelTypeExTransitionAlg[typeEx1][typeEx2] = 0
                        timeLevelTypeExTransitionAlg[typeEx1][typeEx2] = {"times": {}, "nbStudTrans": 0}
                    for tmp in studEx:
                        if str(tmp) not in timeLevelTypeExTransitionAlg[typeEx1][typeEx2]["times"].keys():
                            timeLevelTypeExTransitionAlg[typeEx1][typeEx2]["times"][str(tmp)] = 0
                        timeLevelTypeExTransitionAlg[typeEx1][typeEx2]["times"][str(tmp)] += 1
                    timeLevelTypeExTransitionAlg[typeEx1][typeEx2]["nbStudTrans"] += 1

                    #timeLevelTypeExTransitionAlg[typeEx1][typeEx2] += studEx
                    #timeLevelTypeExTransitionAlg[typeEx1][typeEx2].append(studEx)
    meanTimeLevelTypeExTransitionAlg = {}
    for typeEx1, typeEx2Tab in timeLevelTypeExTransitionAlg.items():
        meanTimeLevelTypeExTransitionAlg[typeEx1] = {}
        for typeEx2, val in typeEx2Tab.items():
            meanTimeLevelTypeExTransitionAlg[typeEx1][typeEx2] = [min(50,int(round(sum([int(val["times"].keys()[x])*val["times"].values()[x] for x in range(len(val["times"].keys()))])*1.0/sum(val["times"].values())))), val["nbStudTrans"]]
                #meanTimeLevelTypeExTransitionAlg[typeEx1][typeEx2] = [min(50,int(round(sum([int(times.keys()[x])*times.values()[x] for x in range(len(times.keys()))])*1.0/sum(times.values())))), sum(times.values())]

    return meanTimeLevelTypeExTransitionAlg #,timeLevelTypeExTransitionAlg

###############################################################################
# Orga transition for all student in a group

def orgaAllStudLevelTypeExTransitionAlg(data): #data : issue to recupDtata()["Datas"]
    allStudentTransition = []
    for c in range(len(data)):
        for user in data[c]:
            allStudentTransition.append(user["transExTypeLevel"])

    return allStudentTransition


###############################################################################
############################ Global Treatment #################################
###############################################################################

def treat_data_exp():
    xp_treated = treat_data("result_xp/data_xp.txt","result_xp")
    plotGlobal(*xp_treated)
    return


def treat_data(path_data = None, directory = "HSSBG_TEST1",studModel = -1):
    all_data = recupData(path_data,directory,studModel)

    print all_data.keys()
    path = all_data["path"]
    nb_stud = all_data["nb_stud"]
    nb_ex_prog = all_data["nb_ex_prog"]
    studModel = all_data["studModel"]
    type_stud = all_data["type_stud"]
    type_algo_tab = all_data["type_algo_tab"]
    r_step = all_data["r_step"]
    RTnames = all_data["RTnames"]
    ref_algo = "%s_%s_r%s" % (type_stud, type_algo_tab, str(r_step))
    print "ref_algo:%s" % ref_algo

    file_data_skill = file(path+"simuSkills.txt",'w')
    datas = all_data["Datas"]
    
    #for i in range(len(datas)):
     #   datas[i] = clust_trans_data(datas[i])

    data_treated = []
    for data in datas:
        orgaData = orgaSeqSkill(data)
        orgaSucc = treatSuccess(orgaSuccess(data))
        orgaSeq =  treatSeqs(orgaData[0],orgaData[-1])
        orgaError = treatErrors(orgaData[0]["CS"])
        data_treated.append([copy.deepcopy(orgaData),copy.deepcopy(orgaSeq),copy.deepcopy(orgaError),copy.deepcopy(orgaSucc)])

    return data_treated,path,nb_stud,nb_ex_prog,studModel,type_stud,type_algo_tab,r_step,RTnames


def manysim(studM = [0,1], tmean = [1], nb_ex_prog = 100, nb_stud = 200):
    for ii in range(len(studM)):
        for i in range(len(tmean)):
            directory = "HSSBG_TEST_NEW2_%s_s" % tmean[i]
            main(directory = directory, nb_ex_prog = nb_ex_prog,nb_stud = nb_stud,studModel=studM[ii], t_mean = tmean[i])
    return 0

# Main functions
def main(nb_stud = 100, studModel = 0, directory = "HSSBG_TEST1", threshold_prob = 0, t_mean = 1, t_var = 1, nb_ex_prog = 100, p_type_lvl = 0, reward_t = 0, motivation = -1, t_learn = 1, type_algo_tab = ["Predefined","ZPDES","RiARiT"], type_algo_plus = [], pop_toUse = None):
    type_algo_tab = type_algo_tab + type_algo_plus

    paths_sims = launch_simulation(nb_stud,studModel,directory,threshold_prob,t_mean,t_var,nb_ex_prog,p_type_lvl,reward_t, motivation, t_learn, type_algo_tab, pop_toUse)
    print "data_treat"
    data_treated = treat_data(paths_sims)
    #plotGlobal(*data_treated, plot_data_sim = 1)

    return data_treated #0

# studModel : 0 -> Q / 1-> P
def launch_simulation(nb_stud = 100, studModel = 0, directory = "HSSBG_TEST1", threshold_prob = 0, t_mean = 1, t_var = 1, nb_ex_prog = 100, p_type_lvl = 0, reward_t = 0, motivation = -1, t_learn = 1, type_algo_tab = ["Predefined","ZPDES","RiARiT"], pop_toUse = None):
    print directory
    print "dat : %s" % threshold_prob
    directory = directory+str(studModel)
    path,path_data = generatePaths(directory)

    #return path_data
    
    data = []
    if studModel != -1 :
        type_stud = ["Q","P"][studModel]
        if pop_toUse == None:
            pop_data = sim.define_population(nb_stud,model = studModel,type_mean = t_mean, type_var = t_var, p_type_lvl = p_type_lvl, type_learn = t_learn)
        for type_algo in type_algo_tab:
            print type_algo
            data.append(sim.simulation(copy.deepcopy(pop_data), nb_stud,model = studModel,thres_prob = threshold_prob, nb_ex = nb_ex_prog, p_type_lvl = p_type_lvl, reward_type = reward_t, motivation = motivation, type_algo = type_algo))

    RTnames  = data[0][0][0]["RT"]

    all_data = {"Datas": data, "type_algo_tab": type_algo_tab,"path": path, "nb_stud": nb_stud,"studModel": studModel,"nb_ex_prog": nb_ex_prog,"type_stud": type_stud,"r_step": reward_t, "RTnames": RTnames}

    jall_data = json.dumps(all_data)
    
    file_simu = file(path_data,'w')
    file_simu.write(jall_data)
    file_simu.close()
    
    #treat_data(path_data)
    
    return path_data

def plotGlobal(dataTreated,path,nb_stud,nb_ex_prog,studModel,type_stud,type_algo_tab,r_step,RTnames, drawSeqCurve = 1, plot_data_sim = 0):
    nbValueParam = dataTreated[0][0][-1]
    print "nbValueParam"
    print nbValueParam
    legendSeq = {}
    RTnames = ["M","R","MM","RM","MAIN","mod","M4","UR","DR","Car","Mmod","M4mod"]#,"CS","OS"]
    RTspe = ["M","R","MM","RM"]
    windows = [10]#,nb_ex_prog+1]
    print "nb_exprog %s" % nb_ex_prog
    # DrawSucces:
    if len(type_algo_tab) == 4 and plot_data_sim ==10:
        for RT in RTnames:
            for i in range(len(windows)):
                succ = []
                if RT in dataTreated[0][3][i].keys():
                    #print "len %s " % len(dataTreated[0][3][i][RT][0][0][0])
                    #print dataTreated[0][3][i][RT][0][0][0]
                    #for 
                    succ.append([dataTreated[0][3][i][RT][0][x][0] for x in range(len(dataTreated[0][3][i][RT][0]))])
                    succ.append([dataTreated[1][3][i][RT][0][x][0] for x in range(len(dataTreated[1][3][i][RT][0]))])
                    succ.append([dataTreated[2][3][i][RT][0][x][0] for x in range(len(dataTreated[2][3][i][RT][0]))])
                    succ.append([dataTreated[3][3][i][RT][0][x][0] for x in range(len(dataTreated[3][3][i][RT][0]))])

                    kG.draw_curve(succ, path = path, labels = [["Random"],["Predefined"], ["ZPDES"], ["RiARiT"]], colors = [["green","green","green","green","#009900","#009900"],["#00BBBB","#00BBBB","#00BBBB","#00BBBB","#0077BB","#0077BB"],["black","black","black","black","#555555","#555555"],['#FF0000','#FF0000','#FF0000','#FF0000','#DD2222','#DD2222']], nb_ex = nb_ex_prog +1, typeData = "successRate" % (), type_data_spe = "%s" % (RT), ref = "window_%s" % (windows[i]), line_type = ['dashed','solid','dashdot','dotted'])
                    #print succ[0]
                    kG.draw_curve([succ[0]], path = path, labels = [["Random"]], colors = [["black","blue","red","#99FF00","#66ccFF","#0055ff"]], nb_ex = nb_ex_prog +1, typeData = "successRate" % (), type_data_spe = "%s" % (RT), ref = "window_%s_random" % (windows[i]), line_type = ['solid'])
                    kG.draw_curve([succ[1]], path = path, labels = [["Predefined"]], colors = [["black","blue","red","#99FF00","#66ccFF","#0055ff"]], nb_ex = nb_ex_prog +1, typeData = "successRate" % (), type_data_spe = "%s" % (RT), ref = "window_%s_predef" % (windows[i]), line_type = ['solid'])
                    kG.draw_curve([succ[2]], path = path, labels = [["ZPDES"]], colors = [["black","blue","red","#99FF00","#66ccFF","#0055ff"]], nb_ex = nb_ex_prog +1, typeData = "successRate" % (), type_data_spe = "%s" % (RT), ref = "window_%s_zpdes" % (windows[i]), line_type = ['solid'])
                    kG.draw_curve([succ[3]], path = path, labels = [["RiARiT"]], colors = [["black","blue","red","#99FF00","#66ccFF","#0055ff"]], nb_ex = nb_ex_prog +1, typeData = "successRate" % (), type_data_spe = "%s" % (RT), ref = "window_%s_riarit" % (windows[i]), line_type = ['solid'])
        
        #return
    #"""
     #   for typeMean in algo[3][1]:
      #      print typeMean
       #     for RT in 
        #Draw Curve Leanning
    if plot_data_sim ==1:
    #if len(type_algo_tab) == 4:

        only_learn = [dataTreated[i][0][1][1] for i in range(len(type_algo_tab))]
        only_learn_label = [type_algo_tab]
        #[dataTreated[0][0][1][1],dataTreated[1][0][1][1],dataTreated[2][0][1][1],dataTreated[3][0][1][1]]
        
        kG.draw_learn_curve(only_learn,path = path,labels = only_learn_label,colors = [["green","#00BBBB","black",'#FF0000'],["green","#00BBBB","black",'#FF0000']],line_type = ['dashed','dashdot','solid',"dotted"], legend_position = 3,ski_lab = ["KnowMoney","IntSum","IntSub","IntDec","DecSum","DecSub","DecDec","Total"],nb_ex = nb_ex_prog)
        
        learn_esti = [dataTreated[i][0][1][0] for i in range(len(type_algo_tab))] + only_learn
        learn_esti_label = [["e%s" % (t) for t in type_algo_tab],["%s" % t for t in type_algo_tab]]
        line_type = ['dashed' for i in range(len(type_algo_tab))] + ['solid'for i in range(len(type_algo_tab))]
        #[dataTreated[0][0][1][0],dataTreated[1][0][1][0],dataTreated[2][0][1][0],dataTreated[3][0][1][0]],[dataTreated[0][0][1][1],dataTreated[1][0][1][1],dataTreated[2][0][1][1],dataTreated[3][0][1][1]]

        #kG.draw_learn_curve(learn_esti,path = path,labels = learn_esti_label,colors = [["green","#00BBBB","black",'#FF0000'][:len(type_algo_tab)],["green","#00BBBB","black",'#FF0000'][:len(type_algo_tab)]],line_type = line_type, legend_position = 3,ski_lab = ["KnowMoney","IntSum","IntSub","IntDec","DecSum","DecSub","DecDec","Total"],nb_ex = nb_ex_prog)


    for RT in RTnames:
        if RT in ["M","R","MM","RM"]:
            legendSeq[RT] = []
            for i in range(dataTreated[0][0][-1][RT][0]):
                legendSeq[RT].append("%s%s" % (RT,i+1))
            tmp = copy.deepcopy(RTspe)
            #tmp.remove("mod")
            #tmp.remove("MAIN")
            tmp.remove(RT)
            for oRT in tmp:
                legendSeq[RT].append(oRT)
    #print legendSeq
    jump_error = 2
    errors_legend = []#("< 5","< 10","< 15","< 20","< 25","< 30","< 35","< 40","< 45","> 45")
    
    for i in range(1,10):
        errors_legend.append("< %s" % (i*jump_error))
    errors_legend.append("> %s" % (11*jump_error))

    for i in range(len(dataTreated)):
        dataToPlotLvlClust = []
        for RT in RTnames:
            if RT in nbValueParam.keys():
                for j in range(len(nbValueParam[RT])):
                    if RT in ["mod","Mmod","M4mod","M4","UR","DR","Car"]:#"M","R","MM","RM","MAIN"
                        a = 0
                        #kG.plot_lvl_curve(dataTreated[i][1][0][RT][j],nb_stud,"%s \nNumber of student doing type %s_%s at each time" % (type_algo_tab[i],RT,j),path = path, ref = "seqCurve_%s_%s_%s" % (RT,type_algo_tab[i],j))
                        #kG.plot_cluster_lvl_sub(dataTreated[i][1][0][RT][j],nb_stud,80, title = "%s \nNumber of student doing type %s_%s at each time" % (type_algo_tab[i],RT,j),path = path, ref = "seq_%s_%s_%s" % (RT,type_algo_tab[i],j))
                        
                    if RT in ["M","R","MM","RM"]:
                        a = 0
                        for k in range(len(dataTreated[i][1][0][RT][j])):
                            if len(dataToPlotLvlClust) <= k:
                                dataToPlotLvlClust.append([])
                            dataToPlotLvlClust[k].append(dataTreated[i][1][0][RT][j][k])
                        #print len(dataTreated[i][1][0][RT][j])
                        #kG.plot_lvl_curve(dataTreated[i][1][1][RT][j][0],nb_stud,"%s \nNumber of student doing type %s_%s at each time" % (type_algo_tab[i],RT,j),path = path, ref = "xseqCurve_%s_%s_%s" % (RT,type_algo_tab[i],j),legend = legendSeq[RT])
                        #kG.plot_cluster_lvl_sub([dataTreated[i][1][1][RT][j]],nb_stud,80, title = "%s \nNumber of student doing type %s_%s at each time" % (type_algo_tab[i],RT,j),path = path, ref = "xseq_%s_%s_%s" % (RT,type_algo_tab[i],j),legend = legendSeq[RT])
        print dataToPlotLvlClust
        kG.plot_lvl(dataTreated[i][2][1][2],nb_stud,nb_ex_prog, title = '%s \nNumber of error (cumulate) made by students' % type_algo_tab[i],legend = errors_legend, path = path, ref = "error_cumulate_time_%s" % type_algo_tab[i])

        kG.plot_cluster_lvl_sub(dataToPlotLvlClust,nb_stud,nb_ex_prog, title = "%s \nStudent distribution per erxercices type over time" % (type_algo_tab[i]),path = path, ref = "clust_xseq_global_%s" % (type_algo_tab[i]),legend = ["M1","M2","M3","M4","M5","M6","R1","R2","R3","R4","MM1","MM2","MM3","MM4","RM1","RM2","RM3","RM4"],dataToUse = range(len(dataToPlotLvlClust)))
        #plot_lvl_curve(dataTreated[i][2][1][2],nb_stud,'%s Number of error (cumulate) made by students' % type_algo_tab[i],errors_legend, path = path, ref = "error_cumulate_time_curve_%s" % type_algo_tab[i])

   # print dataTreated[0][2][1][2]
    
    """
    kG.plot_lvl(data["error_time"][1],nb_stud,'%s \nNumber of error made by students for each type at each time' % keyt,
     path = path, ref = "error_lvl_time_%s" % keyt)
    kG.draw_param_lvl_curve(data["error_time"][1],nb_stud,'%s \n%s of student who made error for each type at each time' % (keyt,"%"),
             path = path, ref = "error_lvl_time_%s" % keyt)
    errors_legend = ("1","2","3","4","5","6","7","8","9","> 10")
    if nb_ex_prog > 50 :
        errors_legend = ("< 5","< 10","< 15","< 20","< 25","< 30","< 35","< 40","< 45","> 45")
    
    kG.plot_lvl(data["error_time"][2],nb_stud,'%s \nNumber of error (cumulate) made by students' % keyt,errors_legend, path = path, ref = "error_cumulate_time_%s" % keyt)
    kG.plot_lvl_curve(data["error_time"][2],nb_stud,'Number of error (cumulate) made by students',errors_legend, path = path, ref = "error_cumulate_time_curve_%s" % keyt)
    """

    #draw_learn_curve([dataTreated[0][0][1][1][0:2],dataTreated[1][0][1][0],dataTreated[2][0][1][0]],[dataTreated[0][0][1][1],dataTreated[1][0][1][1],dataTreated[2][0][1][1]],path = path,labels = [["ePredef","eZPDES","eRiARiT"],["Predefined","ZPDES","RiARiT"]],colors = [["#00BBBB","black",'#FF0000'],["#00BBBB","black",'#FF0000']],line_type = ['dashed','dashed','dashed','solid','solid','solid'], legend_position = 3)

    return



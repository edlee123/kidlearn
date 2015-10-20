#!/usr/bin/python
#-*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        setup
# Purpose:
#
# Author:      Bclement
#
# Created:     14-03-2015
# Copyright:   (c) BClement 2015
# Licence:     GNU Affero General Public License v3.0

#-------------------------------------------------------------------------------
import numpy as np
import copy 
import json
import os
import sys
import kidlearn_lib as k_lib

from kidlearn_lib.config import manage_param as mp

sys.path.append("../..")
import plot_graphics as graph

# example of WorkingSession : one student and one seqequance manager

def do_work_session():
    WorkingSession = k_lib.experimentation.WorkingSession(params_file="worksess_test_1")
    
    return

# example of complete simulation
def do_q_simu():
    simu = k_lib.experimentation.Experiment(params_file="simu_test_1")
    simu.run()

    for seq_name,group in simu._groups.items():

        data = group[0].get_ex_repartition_time(100)
        graph.kGraph.plot_cluster_lvl_sub([data],100,100, title="%s \nStudent distribution per erxercices type over time" % ("test"), path="simulation/graphics/", ref="clust_xseq_global_%s" % (seq_name), legend=["M1","M2","M3","M4","M5","M6","R1","R2","R3","R4","MM1","MM2","MM3","MM4","RM1","RM2","RM3","RM4"], dataToUse=range(len([data])))

# Xp with KT stud model, POMDP, ZPDES, Random %riarit%
def kt_expe(ref_xp="KT_PZR", path_to_save="experimentation/data/", nb_step=51, nb_stud=100, files_to_load=None, ref_bis=""):
    if files_to_load == None:
        files_to_load = {}
    
    def_files_to_load = {}
    def_files_to_load["pomdp"] = {"file_name":"POMDP_{}".format(ref_xp), "path":"data/pomdp"}
    def_files_to_load["stud"] = "stud_{}".format(ref_xp)
    def_files_to_load["zpdes"] = "ZPDES_{}".format(ref_xp)
    def_files_to_load["riarit"] = "RIARIT_{}".format(ref_xp)
    def_files_to_load["random"] = "RANDOM_{}".format(ref_xp)

    ref_xp = "{}_{}".format(ref_xp,ref_bis)

    for key,val in def_files_to_load.items():
        if key not in files_to_load.keys():
            files_to_load[key] = val

    ws_tab_zpdes = []
    ws_tab_riarit = []
    ws_tab_random = []
    ws_tab_pomdp = []
    pomdP = k_lib.seq_manager.POMDP(load_p = files_to_load["pomdp"])
    #pomdP = k_lib.config.datafile.load_file("KT_expe_2","data/pomdp")
    stud = k_lib.student.KTstudent(params_file = files_to_load["stud"])
    zpdes = k_lib.seq_manager.ZpdesHssbg(params_file = files_to_load["zpdes"])
    riarit = k_lib.seq_manager.RiaritHssbg(params_file = files_to_load["riarit"])
    random = k_lib.seq_manager.RandomSequence(params_file = files_to_load["random"])

    for i in range(nb_stud):
        ws_tab_zpdes.append(k_lib.experimentation.WorkingSession(student=copy.deepcopy(stud), seq_manager = copy.deepcopy(zpdes)))
        ws_tab_pomdp.append(k_lib.experimentation.WorkingSession(student=copy.deepcopy(stud), seq_manager = copy.deepcopy(pomdP)))
        ws_tab_riarit.append(k_lib.experimentation.WorkingSession(student=copy.deepcopy(stud), seq_manager = copy.deepcopy(riarit)))
        ws_tab_random.append(k_lib.experimentation.WorkingSession(student=copy.deepcopy(stud), seq_manager = copy.deepcopy(random)))

    wG_zpdes = k_lib.experimentation.WorkingGroup(WorkingSessions = ws_tab_zpdes)
    wG_pomdp = k_lib.experimentation.WorkingGroup(WorkingSessions = ws_tab_pomdp)
    wG_riarit = k_lib.experimentation.WorkingGroup(WorkingSessions = ws_tab_riarit)
    wG_random = k_lib.experimentation.WorkingGroup(WorkingSessions = ws_tab_random)

    wkgs =  {"POMDP" : [wG_pomdp], "ZPDES": [wG_zpdes], "Random": [wG_random], "RIARIT": [wG_riarit]} # {"ZPDES": [wG_zpdes]} # 

    params = {
        "ref_expe" : ref_xp,
        "path_to_save" : path_to_save,
        "seq_manager_list": wkgs.keys(), #"RIARIT"
        "nb_step" : nb_step,
        "population" : {
            "nb_students" : nb_stud,
            "model" : "KT_student",
        }
    }

    xp = k_lib.experimentation.Experiment(WorkingGroups = wkgs, params = params)

    xp.run(nb_step)
    draw_xp_graph(xp,ref_xp,["V1","V2","V3","V4","V5","V6"], nb_ex_type = [1,1,1,1,1,1])
    #all_mean_data = draw_xp_graph(xp,ref_xp)
    #cost = calcul_xp_cost(xp)

    return xp

# Expe to tune ZPDES
def expe_zpdes_promot(ref_xp="kt_multiZ",path_to_save="experimentation/data/", nb_step=100, nb_stud=100):
    zpdes_confs = mp.multi_conf("multi_conf_test","ZPDES_KT6kc","params_files",combine=1)
    
    stud = k_lib.student.KTstudent(params_file="stud_KT6kc")

    zpdes_confs = {mp.generate_diff_config_id(zpdes_confs)[x] : zpdes_confs[x] for x in range(len(zpdes_confs))}

    wkgs = {}
    for ref,conf in zpdes_confs.items():
        zpdes = k_lib.seq_manager.ZpdesHssbg(params=conf)
        wss = []
        for i in range(nb_stud):
            wss.append(k_lib.experimentation.WorkingSession(student=copy.deepcopy(stud), seq_manager=copy.deepcopy(zpdes)))
        wkgs["zpdes_{}".format(ref)] = [k_lib.experimentation.WorkingGroup(WorkingSessions=wss)]

    xp = k_lib.experimentation.Experiment(WorkingGroups=wkgs,
                            ref_expe=ref_xp,
                            path_to_save=path_to_save,
                            seq_manager_list=wkgs.keys(),
                            nb_step=nb_step,
                            population={"nb_students" : nb_stud, 
                                        "model" : "KT_student"})
    xp.run()
    
    draw_xp_graph(xp, ref_xp, ["V1","V2","V3","V4","V5","V6"], nb_ex_type=[1,1,1,1,1,1])

    return xp

def draw_xp_histo(xp, ref_xp, type_ex=["V1","V2","V3","V4","V5"], nb_ex_type=[1,1,1,1,1]):
    # draw histo graph to visualise exercise in time
    for seq_name,group in xp._groups.items():
        data = group[0].get_ex_repartition_time(first_ex= 1, nb_ex=xp.nb_step+1, main_rt = xp.main_act,type_ex = type_ex, nb_ex_type=nb_ex_type)
        graph.kGraph.plot_cluster_lvl_sub([data],xp.nb_students,xp.nb_step, title = "%s \nStudent distribution per erxercices type over time" % (seq_name),path = "%s" % (xp.save_directory), ref = "exTime_%s_%s" % (xp.ref_expe,seq_name),legend = type_ex,dataToUse = range(len([data])), show=0)

def draw_xp_kc_curve(xp):
    # draw learning curve
    skill_labels = xp.KC
    skill_labels.append("All")
    all_mean_data = {seq_name:{} for seq_name in xp._groups.keys()}
    for k in range(len(skill_labels)):
        mean_data = []
        std_data = []
        for seq_name,group in xp._groups.items():
            data = [group[0].get_students_level(time=x, kc=k) for x in range(xp.nb_step)]
            mean_data.append([np.mean(data[x]) for x in range(len(data))])
            std_data.append([np.std(data[x]) for x in range(len(data))])
            all_mean_data[seq_name][skill_labels[k]] = [np.mean(data[x]) for x in range(len(data))]
        
        graph.kGraph.draw_curve([mean_data], labels=[xp._groups.keys()], nb_ex=len(data), typeData="skill_level", type_data_spe="" , ref="%s_%s" %(xp.ref_expe,skill_labels[k]), markers=None, colors=[["#00BBBB","green","black",'#FF0000']], line_type=['dashed','dashdot','solid',"dotted"], legend_position=5, std_data=[std_data], path= "%s" % (xp.save_directory), showPlot=False)


# Script to draw xp graphs
def draw_xp_graph(xp, ref_xp, type_ex=["V1","V2","V3","V4","V5"], nb_ex_type=[1,1,1,1,1]):
    draw_xp_histo(xp,ref_xp,type_ex,nb_ex_type)
    draw_xp_kc_curve(xp)
    
    return 

# calcul xp costs 
def calcul_xp_cost(xp):
    #calcul cost for each student
    cost = xp.calcul_cost()
    mean_cost = {key: np.mean(cost[key]) for key in cost.keys()}
    std_cost = {key: np.std(cost[key]) for key in cost.keys()}
    
    data_cost = {"mean": mean_cost, "std": std_cost}

    path_to_save = "{}/{}".format(xp.save_directory, "cost.txt")

    with open(path_to_save, 'w') as outfile:
        json.dump(data_cost,outfile)

    return data_cost


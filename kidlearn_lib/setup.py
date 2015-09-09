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
import config
import os
import functions as func
import kidlearn_lib as k_lib
import graph_lib as graph


# example of WorkingSession : one student and one seqequance manager

def do_work_session():
    WorkingSession = k_lib.experimentation.WorkingSession(params_file = "worksess_test_1")
    
    return

# example of complete simulation
def do_q_simu():
    simu = k_lib.experimentation.Experiment(params_file = "simu_test_1")
    simu.run()

    for seq_name,group in simu._groups.items():

        data = group[0].get_ex_repartition_time(100)
        graph.kGraph.plot_cluster_lvl_sub([data],100,100, title = "%s \nStudent distribution per erxercices type over time" % ("test"),path = "simulation/graphics/", ref = "clust_xseq_global_%s" % (seq_name),legend = ["M1","M2","M3","M4","M5","M6","R1","R2","R3","R4","MM1","MM2","MM3","MM4","RM1","RM2","RM3","RM4"],dataToUse = range(len([data])))

def kt_expe(ref_xp = "KT_PZR",path_to_save = "experimentation/data/", nb_step = 51, nb_stud = 100):

    stud_tab = []
    zpdes_tab = []
    ws_tab_zpdes = []
    ws_tab_riarit = []
    ws_tab_random = []
    ws_tab_pomdp = []
    pomdP = k_lib.config.datafile.load_file("KT_expe_2","data/pomdp")
    stud = k_lib.student.KTStudent(params_file = "kt2_stud")
    zpdes = k_lib.seq_manager.ZpdesHssbg(params_file = "ZPDES_KT")
    riarit = k_lib.seq_manager.RiaritHssbg(params_file = "RIARIT_KT")
    random = k_lib.seq_manager.RandomSequence(params_file = "Random_KT")

    for i in range(nb_stud):
        ws_tab_zpdes.append(k_lib.experimentation.WorkingSession(student=copy.deepcopy(stud), seq_manager = copy.deepcopy(zpdes)))
        ws_tab_pomdp.append(k_lib.experimentation.WorkingSession(student=copy.deepcopy(stud), seq_manager = copy.deepcopy(pomdP)))
        ws_tab_riarit.append(k_lib.experimentation.WorkingSession(student=copy.deepcopy(stud), seq_manager = copy.deepcopy(riarit)))
        ws_tab_random.append(k_lib.experimentation.WorkingSession(student=copy.deepcopy(stud), seq_manager = copy.deepcopy(random)))

    wG_zpdes = k_lib.experimentation.WorkingGroup(params = {"0":0}, WorkingSessions = ws_tab_zpdes)
    wG_pomdp = k_lib.experimentation.WorkingGroup(params = {"0":0}, WorkingSessions = ws_tab_pomdp)
    wG_riarit = k_lib.experimentation.WorkingGroup(params = {"0":0}, WorkingSessions = ws_tab_riarit)
    wG_random = k_lib.experimentation.WorkingGroup(params = {"0":0}, WorkingSessions = ws_tab_random)

    wgroups = {"POMDP" : [wG_pomdp], "ZPDES": [wG_zpdes], "Random": [wG_random]} # "RIARIT": [wG_riarit]

    params = {
        "ref_expe" : ref_xp,
        "path_to_save" : path_to_save,
        "seq_manager_list":["POMDP","ZPDES","Random"], #"RIARIT"
        "nb_step" : nb_step,
        "population" : {
            "nb_students" : nb_stud,
            "model" : "KT_student",
        }
    }

    xp = k_lib.experimentation.Experiment(WorkingGroups = wgroups, params = params)

    xp.run(nb_step)

    for seq_name,group in xp._groups.items():
        data = group[0].get_ex_repartition_time(first_ex= 1, nb_ex=nb_step+1, main_rt = "KT1",type_ex = ["V1","V2","V3","V4","V5"],nb_ex_type=[1,1,1,1,1])
        graph.kGraph.plot_cluster_lvl_sub([data],nb_stud,nb_step, title = "%s \nStudent distribution per erxercices type over time" % (seq_name),path = "%s/%s" % (xp._directory, ref_xp), ref = "clust_xseq_global_%s" % (seq_name),legend = ["V1","V2","V3","V4","V5"],dataToUse = range(len([data])), show=0)

    skill_labels = ["S1","S2","S3","S4","S5","All"]
    all_mean_data = {seq_name:{} for seq_name in xp._groups.keys()}
    for k in range(len(skill_labels)):
        mean_data = []
        std_data = []
        for seq_name,group in xp._groups.items():
            data = [group[0].get_students_level(time = x, kc = k) for x in range(nb_step)]
            mean_data.append([np.mean(data[x]) for x in range(len(data))])
            std_data.append([np.std(data[x]) for x in range(len(data))])
            all_mean_data[seq_name][skill_labels[k]] = [np.mean(data[x]) for x in range(len(data))]
        
        graph.kGraph.draw_curve([mean_data], labels = [xp._groups.keys()], nb_ex = len(data), typeData = "skill_level", type_data_spe = "" ,ref = skill_labels[k], markers = None, colors = [["#00BBBB","green","black",'#FF0000']], line_type = ['dashed','dashdot','solid',"dotted"], legend_position = 2, std_data = [std_data], path = "%s/%s" % (xp._directory, ref_xp),showPlot = False)

    return xp,all_mean_data

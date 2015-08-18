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

def kt_expe(ref_xp = "KT_PZR",path_to_save = "experimentation/data/"):

    stud_tab = []
    zpdes_tab = []
    ws_tab_zpdes = []
    ws_tab_riarit = []
    ws_tab_pomdp = []
    pomdP = k_lib.config.datafile.load_file("KT_expe_1","data/pomdp")
    stud = k_lib.student.KTStudent()
    zpdes = k_lib.seq_manager.ZpdesHssbg(params_file = "ZPDES_KT")
    riarit = k_lib.seq_manager.RiaritHssbg(params_file = "RIARIT_KT")

    for i in range(100):
        ws_tab_zpdes.append(k_lib.experimentation.WorkingSession(student=copy.deepcopy(stud), seq_manager = copy.deepcopy(zpdes)))
        ws_tab_pomdp.append(k_lib.experimentation.WorkingSession(student=copy.deepcopy(stud), seq_manager = copy.deepcopy(pomdP)))
        ws_tab_riarit.append(k_lib.experimentation.WorkingSession(student=copy.deepcopy(stud), seq_manager = copy.deepcopy(riarit)))

    wG_zpdes = k_lib.experimentation.WorkingGroup(params = {"0":0}, WorkingSessions = ws_tab_zpdes)
    wG_pomdp = k_lib.experimentation.WorkingGroup(params = {"0":0}, WorkingSessions = ws_tab_pomdp)
    wG_riarit = k_lib.experimentation.WorkingGroup(params = {"0":0}, WorkingSessions = ws_tab_riarit)

    wgroups = {"POMDP" : [wG_pomdp], "ZPDES": [wG_zpdes], "RIARIT": [wG_riarit]}

    params = {
        "ref_expe" : ref_xp,
        "path_to_save" : path_to_save,
        "seq_manager_list":["POMDP","ZPDES","RIARIT"],
        "nb_step" : 50,
        "population" : {
            "nb_students" : 100,
            "model" : "KT_student",
        }
    }

    xp = k_lib.experimentation.Experiment(WorkingGroups = wgroups, params = params)

    xp.run(51)

    skill_labels = ["S1","S2","S3","S4","S5","All"]
    for k in range(len(skill_labels)):
        mean_data = []
        std_data = []
        for seq_name,group in xp._groups.items():

                data = [group[0].get_students_level(time = x, kc = k) for x in range(51)]
                mean_data.append([np.mean(data[x]) for x in range(len(data))])
                std_data.append([np.std(data[x]) for x in range(len(data))])

        graph.kGraph.draw_curve([mean_data], labels = [xp._groups.keys()], nb_ex = len(data), typeData = "skill_level", type_data_spe = "" ,ref = skill_labels[k], markers = None, colors = [["#00BBBB","green",'#FF0000',"black"]], line_type = ['dashed','dashdot','solid',"dotted"], legend_position = 3, std_data = [std_data], path = "%s/%s" % (xp._directory, ref_xp),showPlot = False)


    return xp


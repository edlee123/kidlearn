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
import scipy.optimize as soptimize
import uuid

from kidlearn_lib.config import manage_param as mp
from experiment_manager.job_queue import get_jobqueue
from experiment_manager.job import IteratedJob

sys.path.append("../..")
import plot_graphics as graph

# example of WorkingSession : one student and one seqequance manager

#########################################################
#########################################################
# Xp on Avakas
#########################################################

def avakas_xp(objs_to_job):
    jq_config = {
        'jq_type': 'avakas',
        'ssh_cfg':{'username':'bclement'},
        'max_jobs' : 100
    }

    jq = get_jobqueue(**jq_config)

    kidleanrUrl = '-e git+https://github.com/flowersteam/kidlearn.git@origin/feature/xp_script#egg=kidlearn_lib'
    expeManageUrl = '-e git+https://github.com/wschuell/experiment_manager.git@origin/develop#egg=experiment_manager'
    jrequirements = [expeManageUrl,kidleanrUrl]

    for obj in objs_to_job:
        file_to_save = obj.uuid+".dat"
        jq.add_job(IteratedJob(filename=file_to_save, obj=obj,step_fun="step_forward",steps=100,estimated_time = 3600,virtual_env="test",requirements=jrequirements))

    return jq

def gen_conf_to_optimize(save_path="experimentation/optimize/multiconf/"):
    
    filter1_vals = [round(x,1) for x in np.arange(0.1,0.9,0.2)]
    stepUp_vals = range(4,10,2)
    upZPD_vals = [round(x,1) for x in np.arange(0.3,0.7,0.1)]
    deact_vals = [round(x,1) for x in np.arange(0.5,0.9,0.1)]
    prom_coef_vals = [round(x,1) for x in np.arange(0.2,2,0.3)]

    multi_confs = {
        "ZpdesSsbg": {
            "ZpdesSsb": {
                "filter1": filter1_vals,
                "stepUpdate" : stepUp_vals,
                "upZPDval" : upZPD_vals,
                "deactZPDval" : deact_vals,
                "promote_coeff" : prom_coef_vals,
            }
        }
    }

    zpdes_confs = mp.multi_conf(base_param_file="ZPDES_KT6kc",directory="params_files/ZPDES",multi_params=multi_confs, combine=1)
    #conf_ids = mp.generate_diff_config_id(zpdes_confs)
    #zpdes_confs = {conf_ids[x] : zpdes_confs[x] for x in range(len(zpdes_confs))}
    uid = str(uuid.uuid1())

    jstr = json.dumps(zpdes_confs)
    
    k_lib.config.datafile.create_directories([save_path])
    save_path = save_path + "KT6kc_all_confs.json"
    k_lib.functions.write_in_file(save_path,jstr)

    return zpdes_confs

def gen_xp_to_optimize(zpdes_confs,ref_xp="optimize",nb_stud=1000,nb_step=100, base_path_to_save="experimentation/data/"):
    stud = k_lib.student.KTstudent(params_file="stud_KT6kc",directory="params_files/studModel")

    wkgs = {}
    for ref,conf in zpdes_confs.items():
        zpdes = k_lib.seq_manager.ZpdesHssbg(params=conf)
        wss = []
        for k in range(nb_stud):
            wss.append(k_lib.experimentation.WorkingSession(student=copy.deepcopy(stud), seq_manager=copy.deepcopy(zpdes)))
        wkgs["zpdes_{}".format(ref)] = [k_lib.experimentation.WorkingGroup(WorkingSessions=wss)]

    xp = k_lib.experimentation.Experiment(WorkingGroups=wkgs,
                        ref_expe=ref_xp,
                        path_to_save=base_path_to_save,
                        seq_manager_list=wkgs.keys(),
                        nb_step=nb_step,
                        population={"nb_students" : nb_stud, 
                                    "model" : "KT_student"})
    return xp


def optimize_zpdes_on_avakas(base_ref_xp="optimize",nb_stud=1000,nb_step=100, base_path_to_save="experimentation/data/"):
    zpdes_confs = k_lib.functions.load_json("KT6kc_all_confs","experimentation/optimize/multiconf/")

    zpdes_to_test = zpdes_confs[0:10]
    
    conf_ids = mp.generate_diff_config_id(zpdes_to_test)
    zpdes_to_test = {conf_ids[x] : zpdes_to_test[x] for x in range(len(zpdes_to_test))}

    xp_list = [gen_xp_to_optimize(zpdes_to_test)]

    jq = avakas_xp(xp_list)

    #xp_list=[]
    #nb_group_per_xp = 10
    #nb_conf_to_test = 10 #len(zpdes_confs)
    #for i in range(nb_conf_to_test/nb_group_per_xp):
    #    if nb_group_per_xp < len(zpdes_confs)-i*nb_group_per_xp: 
    #        nb_conf = nb_group_per_xp
    #    else:
    #        nb_conf = nb_group_per_xp - len(zpdes_confs)-i*nb_group_per_xp
    #    
   

    return jq

#########################################################
# Xp on Avakas
#########################################################
#########################################################

def calcul_cost_zpdes(zpdes_param,nb_stud = 100,nb_step = 100):
    print zpdes_param

    params = {
    "algo_name" : "ZpdesHssbg",
    "graph": { 
        "file_name" :"KT6kc_graph",
        "path" : "graph/",
        "main_act" : "KT6kc"
        },
    
    "ZpdesSsbg": {
        "ZpdesSsb" :{
            "filter1": zpdes_param[0], 
            "filter2": 1-zpdes_param[0], 
            "uniformval": 0.05,
            "stepUpdate" : int(zpdes_param[2]),
            "upZPDval" : zpdes_param[3],
            "deactZPDval" : zpdes_param[4],
            "promote_coeff" : zpdes_param[5],
            "thresHierarProm" : 0.3,
            "h_promote_coeff" : 1,
            "thresZBegin" : 0.4,
            "size_window": 3,
            "spe_promo" : 0
            }
        }
    }

    stud = k_lib.student.KTstudent(params_file="stud_KT6kc",directory="params_files/studModel")
    zpdes = k_lib.seq_manager.ZpdesHssbg(params=params)
    ws_tab_zpdes = []
    for i in range(nb_stud):
        ws_tab_zpdes.append(k_lib.experimentation.WorkingSession(student=copy.deepcopy(stud), seq_manager = copy.deepcopy(zpdes)))
    wG_zpdes = k_lib.experimentation.WorkingGroup(WorkingSessions = ws_tab_zpdes)
    wG_zpdes.run(nb_step)
    print np.mean(wG_zpdes.calcul_cost())
    return np.mean(wG_zpdes.calcul_cost())


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
    zpdes_confs = mp.multi_conf("multi_conf_test","ZPDES_KT6kc","params_files/ZPDES",combine=1)
    
    stud = k_lib.student.KTstudent(params_file="stud_KT6kc",directory="params_files/studModel")

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
    xp.save()
    draw_xp_graph(xp, ref_xp, ["V1","V2","V3","V4","V5","V6"], nb_ex_type=[1,1,1,1,1,1])

    return xp

def draw_xp_histo(xp, ref_xp, type_ex=["V1","V2","V3","V4","V5"], nb_ex_type=[1,1,1,1,1]):
    # draw histo graph to visualise exercise in time
    for seq_name,group in xp._groups.items():
        data = group[0].get_ex_repartition_time(first_ex= 1, nb_ex=xp.nb_step+1, main_rt = xp.main_act,type_ex = type_ex, nb_ex_type=nb_ex_type)
        graph.kGraph.plot_cluster_lvl_sub([data],xp.nb_students,xp.nb_step, title = "%s \nStudent distribution per erxercices type over time" % (seq_name),path = "%s" % (xp.save_path), ref = "exTime_%s_%s" % (xp.ref_expe,seq_name),legend = type_ex,dataToUse = range(len([data])), show=0)

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
        
        graph.kGraph.draw_curve([mean_data], labels=[xp._groups.keys()], nb_ex=len(data), typeData="skill_level", type_data_spe="" , ref="%s_%s" %(xp.ref_expe,skill_labels[k]), markers=None, colors=[["#00BBBB","green","black",'#FF0000']], line_type=['dashed','dashdot','solid',"dotted"], legend_position=5, std_data=[std_data], path= "%s" % (xp.save_path), showPlot=False)


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

    path_to_save = "{}/{}".format(xp.save_path, "cost.txt")

    with open(path_to_save, 'w') as outfile:
        json.dump(data_cost,outfile)

    return data_cost


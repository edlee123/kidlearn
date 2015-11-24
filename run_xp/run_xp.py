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
from kidlearn_lib import functions as func
from experiment_manager.job_queue import get_jobqueue
from experiment_manager.job.kidlearn_job import  KidlearnJob

sys.path.append("../..")
import plot_graphics as graph

import matplotlib.pyplot as plt
import matplotlib.cm as cm

# example of WorkingSession : one student and one sequence manager

#########################################################
#########################################################
# Xp on Avakas
#########################################################

def avakas_xp(objs_to_job=None):
    jq_config = {
        'jq_type': 'avakas',
        'ssh_cfg':{'username':'bclement'},
        'max_jobs' : 350,
        'auto_update': False
    }

    jq = get_jobqueue(**jq_config)

    kidleanrUrl = '-e git+https://github.com/flowersteam/kidlearn.git@origin/feature/xp_script#egg=kidlearn_lib'
    expeManageUrl = '-e git+https://github.com/wschuell/experiment_manager.git@origin/feature/ben_jobs#egg=experiment_manager'
    jrequirements = [expeManageUrl,kidleanrUrl]

    if objs_to_job != None :
        for obj in objs_to_job:
            file_to_save = obj.uuid+".dat"
            jq.add_job(KidlearnJob(descr=jq.name, filename=file_to_save, obj=obj,step_fun="step_forward",steps=100,estimated_time = 5400,virtual_env="test",requirements=jrequirements))
        jq.check_virtualenvs()
    return jq

def local_xp(objs_to_job=None):
    jq_config = {
        'jq_type': 'local',
    }

    jq = get_jobqueue(**jq_config)

    if objs_to_job != None :
        for obj in objs_to_job:
            file_to_save = obj.uuid+".dat"
            jq.add_job(KidlearnJob(descr=jq.name, filename=file_to_save, obj=obj, step_fun="step_forward", steps=100, estimated_time = 3600))

    return jq

def all_values_zpdes():
    filter1_vals = [round(x,1) for x in np.arange(0.1,0.6,0.1)]
    stepUp_vals = range(4,8,1)
    upZPD_vals = [round(x,1) for x in np.arange(0.3,0.8,0.1)]
    deact_vals = [round(x,1) for x in np.arange(0.4,0.9,0.1)]
    prom_coef_vals = [round(x,1) for x in np.arange(0.2,2,0.2)]

    return filter1_vals, stepUp_vals, upZPD_vals, deact_vals, prom_coef_vals

def gen_conf_to_optimize(save_path="experimentation/optimize/multiconf/", main_act = "KT6kc"):
    
    filter1_vals, stepUp_vals, upZPD_vals, deact_vals, prom_coef_vals = all_values_zpdes()

    print filter1_vals
    print stepUp_vals
    print upZPD_vals
    print deact_vals
    print prom_coef_vals


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

    base_conf = func.load_json("ZPDES_base","params_files/ZPDES")
    base_conf["graph"]["file_name"] = "{}_graph".format(main_act)
    base_conf["graph"]["main_act"] = main_act

    base_conf["graph"].update(func.load_json(base_conf["graph"]["file_name"],base_conf["graph"]["path"]))
    zpdes_confs = mp.multi_conf(base_conf=base_conf, multi_params=multi_confs, combine=1)

    #conf_ids = mp.generate_diff_config_id(zpdes_confs)
    #zpdes_confs = {conf_ids[x] : zpdes_confs[x] for x in range(len(zpdes_confs))}
    uid = str(uuid.uuid1())

    jstr = json.dumps(zpdes_confs)
    
    k_lib.config.datafile.create_directories([save_path])
    save_path = "{}{}_all_confs.json".format(save_path,main_act)
    k_lib.functions.write_in_file(save_path,jstr)

    return zpdes_confs

def gen_xp_to_optimize(zpdes_confs,ref_xp="optimize",nb_stud=1000,nb_step=100, base_path_to_save="experimentation/data/"):
    studconf = func.load_json(params_file="stud_KT6kc",directory="params_files/studModel")
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


def gen_set_zpdes_confs(nb_group_per_xp=10, nb_conf_to_test = None, main_act="KT6kc"):
    all_confs_file_path = "experimentation/optimize/multiconf/"
    all_confs_file = "{}_all_confs.json".format(main_act)
    print os.path.join(all_confs_file_path,all_confs_file)

    if os.path.isfile(os.path.join(all_confs_file_path,all_confs_file)):
        all_zpdes_confs = k_lib.functions.load_json(all_confs_file, all_confs_file_path)
    else: 
        all_zpdes_confs = gen_conf_to_optimize(all_confs_file_path,main_act)

    all_conf_ids = mp.generate_diff_config_id(all_zpdes_confs)
    nb_conf_to_test = nb_conf_to_test or len(all_zpdes_confs)

    set_zpdes_confs = []

    for i in range(nb_conf_to_test/nb_group_per_xp):
        if nb_group_per_xp <= len(all_zpdes_confs)-i*nb_group_per_xp: 
            nb_conf = nb_group_per_xp
        else:
            nb_conf = nb_group_per_xp - len(all_zpdes_confs)-i*nb_group_per_xp

        first_conf = i*nb_group_per_xp
        last_conf = i*nb_group_per_xp + nb_conf

        zpdes_conf = all_zpdes_confs[first_conf:last_conf]
        #print "i %s nbconf %s, z %s" % (i, nb_conf,len(zpdes_conf))

        conf_ids = all_conf_ids[first_conf:last_conf]

        zpdes_conf = {conf_ids[x] : zpdes_conf[x] for x in range(len(zpdes_conf))}
        set_zpdes_confs.append(zpdes_conf)

    return set_zpdes_confs

def gen_stud_confs(nb_students=1000, perturbated=0, params_file="stud_KT6kc_0"):
    studconf = func.load_json(params_file,"params_files/studModel")
    if perturbated == 1 :
        pass
    else:
        stud_confs = [copy.deepcopy(studconf) for x in range(nb_students)]

    return stud_confs

def xp_conf_to_job(zpdes_conf,stud_confs, nb_step=100,studFile=""):
    xp_conf = {}
    xp_conf["zpdes_conf"] = zpdes_conf
    xp_conf["stud_confs"] = stud_confs
    xp_conf["nb_steps"] = nb_step
    xp_conf["stud_file"] = studFile

    return xp_conf



def full_optimize_zpdes(nb_group_per_xp=10,nb_stud=1000, nb_step=100,xp_type=0, nb_conf_to_test = None, stud_file="stud_KT6kc_0"):

    if xp_type == 1: jq = avakas_xp()
    else: jq = local_xp()

    kidleanrUrl = '-e git+https://github.com/flowersteam/kidlearn.git@origin/feature/xp_script#egg=kidlearn_lib'
    expeManageUrl = '-e git+https://github.com/wschuell/experiment_manager.git@origin/feature/ben_jobs#egg=experiment_manager'
    jrequirements = [expeManageUrl,kidleanrUrl]

    set_zpdes_conf = gen_set_zpdes_confs(nb_group_per_xp,nb_conf_to_test)

    for set_zpdes in set_zpdes_conf:
        stud_confs = gen_stud_confs(nb_students=nb_stud, params_file=stud_file)
        xp_conf = xp_conf_to_job(set_zpdes,stud_confs, nb_step=nb_step, studFile=stud_file)

        #file_to_save = xp.uuid+".dat"
        if xp_type == 1:
            jq.add_job(KidlearnJob(descr=jq.name, filename="data.dat", obj=xp_conf,step_fun="step_forward",steps=100,estimated_time = 5400,virtual_env="test",requirements=jrequirements))
        else:
            jq.add_job(KidlearnJob(descr=jq.name, filename="data.dat", obj=xp_conf, step_fun="step_forward", steps=100, estimated_time = 3600))

    if xp_type == 1:
        jq.check_virtualenvs()
        #xp_list.append(xp_to_job(first_conf=first_conf, last_conf=last_conf, zpdes_confs = zpdes_confs, conf_ids = conf_ids, nb_stud=nb_stud, nb_step=nb_step))

    return jq

def cost_evol_conf(cost_mean, ref_conf):
    conf_dict_cost = []
    for key,val in cost_mean.items():
        conf_dict_cost.append(find_zpdes_conf(key,val))

    return conf_dict_cost

def find_zpdes_conf(confkey,cost=None):
    #for confkey,val in cost_mean.items():
    strconf = func.spe_split('_',confkey)[1]
    paramsconf = func.spe_split('[0-9]',strconf)
    valsconf = func.spe_split('[a-z]',strconf)
    values = {}
    for key,val in zip(paramsconf,valsconf):
        if int(val) > 100:
            val = val[1:]

        if key != "se":
            val = "{}.{}".format(val[0],val[1:])

        if val[0] == "0" and val[1] != ".":
            val = "{}.{}".format(val[0],val[1:])

        values[key] = float(val)
    if cost != None:
        values["cost"]=cost

    return values

#########################################################
# Xp on Avakas
#########################################################
#########################################################

def perturbated_population(zpdes_confs,ref_xp="perturbation",nb_step=100, base_path_to_save="experimentation/data/"):
    population_conf = func.load_json(params_file="perturbation_KT6kc",directory="params_files/studModel")
    population = k_lib.student.Population(params=population_conf)
    nb_stud = population.nb_students

    wkgs = {}
    for ref,conf in zpdes_confs.items():
        zpdes = k_lib.seq_manager.ZpdesHssbg(params=conf)
        wss = []
        for k in range(nb_stud):
            wss.append(k_lib.experimentation.WorkingSession(student=copy.deepcopy(population.students[k])), seq_manager=copy.deepcopy(zpdes))
        wkgs["zpdes_{}".format(ref)] = [k_lib.experimentation.WorkingGroup(WorkingSessions=wss)]

    xp = k_lib.experimentation.Experiment(WorkingGroups=wkgs,
                        ref_expe=ref_xp,
                        path_to_save=base_path_to_save,
                        seq_manager_list=wkgs.keys(),
                        nb_step=nb_step,
                        population={"nb_students" : nb_stud, 
                                    "model" : "KT_student"})
    return xp



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

def change_graph_params(params,graph_file,main_act):
    params["graph"]["file_name"] = graph_file
    params["graph"]["main_act"] = main_act
    return params

# Xp with KT stud model, POMDP, ZPDES, Random %riarit%
def kt_expe(ref_xp="KT6kc", path_to_save="experimentation/data/", nb_step=100, nb_stud=100, files_to_load=None, ref_bis="", disruption_pop_file="perturbation_KT6kc",disruption=0, ref_pomdp="_2", ref_stud="_2"):
    if files_to_load == None:
        files_to_load = {}
    
    def_files_to_load = {}
    def_files_to_load["pomdp"] = {"file_name":"POMDP_{}{}".format(ref_xp,ref_pomdp), "path":"data/pomdp"}
    def_files_to_load["stud"] = "stud_{}{}".format(ref_xp,ref_stud)
    def_files_to_load["zpdes"] = "ZPDES_{}".format(ref_xp)
    #def_files_to_load["riarit"] = "RIARIT_{}".format(ref_xp)
    def_files_to_load["random"] = "RANDOM_{}".format(ref_xp)

    ref_xp = "{}_{}".format(ref_xp,ref_bis)

    for key,val in def_files_to_load.items():
        if key not in files_to_load.keys():
            files_to_load[key] = val

    
    pomdP = k_lib.seq_manager.POMDP(load_p = files_to_load["pomdp"])
    
    #pomdP = k_lib.config.datafile.load_file("KT_expe_2","data/pomdp")
    
    zpdes_params2 = {
        "algo_name" : "ZpdesHssbg",
        "graph": { 
            "file_name" :"KT6kc_graph",
            "path" : "graph/",
            "main_act" : "KT6kc"
            },
        
        "ZpdesSsbg": {
            "ZpdesSsb": {
                "filter1": 0.4,# 0.30,
                "uniformval": 0.05,# 0.05,
                "stepUpdate" : 6,# 6,
                "upZPDval" : 0.6,# 0.6,
                "deactZPDval" : 0.4,# 0.5,
                "promote_coeff" : 14,# 1.7,
                "thresHierarProm" : 0.5,# 0.5,
                "h_promote_coeff" : 0.25,# 0.25,
                "size_window": 3,# 3,
                "spe_promo": 0# 0
            }
        }
    }

    #population_conf = func.load_json()
    population = k_lib.student.Population(params_file=disruption_pop_file,directory="params_files/studModel")
    #stud = k_lib.student.KTstudent(params=population.base_model)
    stud = k_lib.student.KTstudent(params_file = files_to_load["stud"],directory="params_files/studModel")
    nb_stud = population.nb_students

    zpdes_params = func.load_json(file_name=files_to_load["zpdes"],dir_path="params_files/ZPDES")
    zpdes = k_lib.seq_manager.ZpdesHssbg(zpdes_params)#params=zpdes_params)
    zpdes2 = k_lib.seq_manager.ZpdesHssbg(zpdes_params2)#params=zpdes_params)
    #riarit = k_lib.seq_manager.RiaritHssbg(params_file=files_to_load["riarit"],directory="params_files/RIARIT")
    random = k_lib.seq_manager.RandomSequence(params_file=files_to_load["random"],directory="params_files/RANDOM")

    ws_tab_zpdes = []
    ws_tab_zpdes2 = []
    ws_tab_riarit = []
    ws_tab_random = []
    ws_tab_pomdp = []

    for i in range(nb_stud):
        if disruption == 1:
            stud = population.students[i]
        ws_tab_zpdes.append(k_lib.experimentation.WorkingSession(student=copy.deepcopy(stud), seq_manager = copy.deepcopy(zpdes)))
        ws_tab_zpdes2.append(k_lib.experimentation.WorkingSession(student=copy.deepcopy(stud), seq_manager = copy.deepcopy(zpdes2)))
        ws_tab_pomdp.append(k_lib.experimentation.WorkingSession(student=copy.deepcopy(stud), seq_manager = copy.deepcopy(pomdP)))
        #ws_tab_riarit.append(k_lib.experimentation.WorkingSession(student=copy.deepcopy(stud), seq_manager = copy.deepcopy(riarit)))
        ws_tab_random.append(k_lib.experimentation.WorkingSession(student=copy.deepcopy(stud), seq_manager = copy.deepcopy(random)))

    wG_zpdes = k_lib.experimentation.WorkingGroup(WorkingSessions = ws_tab_zpdes)
    wG_zpdes2 = k_lib.experimentation.WorkingGroup(WorkingSessions = ws_tab_zpdes2)
    wG_pomdp = k_lib.experimentation.WorkingGroup(WorkingSessions = ws_tab_pomdp)
    #wG_riarit = k_lib.experimentation.WorkingGroup(WorkingSessions = ws_tab_riarit)
    wG_random = k_lib.experimentation.WorkingGroup(WorkingSessions = ws_tab_random)

    wkgs =  {"POMDP" : [wG_pomdp], "ZPDES": [wG_zpdes], "Random": [wG_random], "ZPDES2": [wG_zpdes2]}#, "RIARIT": [wG_riarit]} # {"ZPDES": [wG_zpdes]} # 

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

#############################################################################
# Cost 
#############################################################################

def recup_mean_cost_from_jq(jq=None, jq_uuid=None):
    jq_uuid = jq_uuid or jq.uuid
    allcost_name = "all_cost_"+jq_uuid
    allcost = k_lib.func.load_json(allcost_name)
    nc = calcul_xp_cost(cost=allcost)
    cost_mean = copy.deepcopy(nc["mean"])

    return cost_mean


# calcul xp costs 
def calcul_xp_cost(xp = None, cost = None):
    #calcul cost for each student
    if cost is not None:
        cost = cost
        path_to_save = "mean_std_cost.json"
    else:
        cost = xp.calcul_cost()
        path_to_save = "{}/{}".format(xp.save_path, "cost.txt")
    mean_cost = {key: np.mean(cost[key]) for key in cost.keys()}
    std_cost = {key: np.std(cost[key]) for key in cost.keys()}
    
    data_cost = {"mean": mean_cost, "std": std_cost}


    with open(path_to_save, 'w') as outfile:
        json.dump(data_cost,outfile)

    return data_cost

def curve_cost_evolv(cost_mean):
    filter1_vals, stepUp_vals, upZPD_vals, deact_vals, prom_coef_vals = all_values_zpdes()

    dict_cost_conf = {}
    opti_conf_key = find_opti_conf(cost_mean)[0]

    opti_conf = find_zpdes_conf(opti_conf_key)#,cost=cost_mean[opti_conf_key])

    val_tab_to_curve = {}

    for key in opti_conf.keys():
        val_tab_to_curve[key]=[]
        for confkey,cost in cost_mean.items():
            conf = find_zpdes_conf(confkey)#,cost=cost)
            equal = 0
            for key2 in opti_conf.keys():
                #print "key {} key2 {}".format(key,key2)
                if key2 != key and conf[key2] == opti_conf[key2]:
                    equal += 1
            if equal == len(opti_conf.keys())-1:
                val_tab_to_curve[key].append((conf[key],cost))
        val_tab_to_curve[key].sort()
    return val_tab_to_curve


def find_opti_conf(cost_mean):

    max_val_key = []
    for key,val in cost_mean.items():
        if val == max(cost_mean.values()):
            max_val_key.append(key)

    return max_val_key

def curve_cost_val_compare_conf(conf_val):
    for key,val in conf_val.items():
        plt.cla()
        plt.clf()
        print key
        plt.close()
        plt.plot([valu[0] for valu in val],[valu[1] for valu in val])
        plt.show()

def gen_all_pomdp():
    pomdp_model_base = k_lib.func.load_json("POMDP_KT6kc","params_files/POMDP")
    for nbKc in [10]: #2,3,4,5,7,
        print nbKc
        pomdp_model = copy.deepcopy(pomdp_model_base)
        pomdp_model["ref"] = "KT{}kc_0".format(nbKc)
        pomdp_model["action"] = "KT{}kc".format(nbKc)
        pomdp_model["n_Action"] = nbKc
        pomdp_model["learn_model"]["file_name"] = "stud_KT{}kc_0".format(nbKc)
        path = "params_files/POMDP/POMDP_KT{}kc.json".format(nbKc)
        func.write_in_file(path,json.dumps(pomdp_model))
        pomdp = k_lib.seq_manager.POMDP(params = pomdp_model, save_pomdp=1)



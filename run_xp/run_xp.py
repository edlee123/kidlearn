#!/usr/bin/python
# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------------
# Name:        setup
# Purpose:
#
# Author:      Bclement
#
# Created:     14-03-2015
# Copyright:   (c) BClement 2015
# Licence:     GNU Affero General Public License v3.0

# -------------------------------------------------------------------------------
import numpy as np
import copy
import json
import os
import sys
import kidlearn_lib as k_lib
import scipy.optimize as soptimize
import scipy.stats as sstats
import uuid
import itertools
import scipy.io

from scipy.optimize import curve_fit
from kidlearn_lib.config import manage_param as mp
from kidlearn_lib import functions as func
from experiment_manager.job_queue import get_jobqueue
from experiment_manager.job.kidlearn_job import KidlearnJob
from experiment_manager.job.classic_job import ClassicJob
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import cPickle

sys.path.append("../..")
import plot_graphics as graph

# example of WorkingSession : one student and one sequence manager

#########################################################
#########################################################
# Xp on Avakas
#########################################################


def avakas_xp(objs_to_job=None):
    jq_config = {
        'jq_type': 'avakas',
        'ssh_cfg': {'username': 'bclement'},
        'max_jobs': 1000,
        'auto_update': False
    }

    jq = get_jobqueue(**jq_config)

    kidleanrUrl = '-e git+https://github.com/flowersteam/kidlearn.git@origin/feature/xp_script#egg=kidlearn_lib'
    expeManageUrl = '-e git+https://github.com/wschuell/experiment_manager.git@origin/feature/ben_jobs#egg=experiment_manager'
    jrequirements = [expeManageUrl, kidleanrUrl]

    if objs_to_job is not None:
        for obj in objs_to_job:
            file_to_save = obj.uuid + ".dat"
            jq.add_job(KidlearnJob(descr=jq.name, filename=file_to_save, obj=obj, step_fun="step_forward", steps=100, estimated_time=5400, virtual_env="test", requirements=jrequirements, path=jq.jobsdir, jq_path=jq.basedir))
        jq.check_virtualenvs()
    return jq


def local_xp(objs_to_job=None):
    jq_config = {
        'jq_type': 'local',
    }

    jq = get_jobqueue(**jq_config)
    print jq.jobsdir
    print jq.basedir

    if objs_to_job is not None:
        for obj in objs_to_job:
            file_to_save = obj.uuid + ".dat"
            jq.add_job(KidlearnJob(descr=jq.name, filename=file_to_save, obj=obj, step_fun="step_forward", steps=100, estimated_time=3600, path=jq.jobsdir, jq_path=jq.basedir))

    return jq


def all_values_zpdes(hierarUtile=0):
    filter1_vals = [round(x, 1) for x in np.arange(0.1, 0.6, 0.1)]
    stepUp_vals = range(4, 7, 1)
    upZPD_vals = [round(x, 1) for x in np.arange(0.5, 0.8, 0.1)]
    deact_vals = [round(x, 1) for x in np.arange(0.4, 0.8, 0.1)]
    prom_coef_vals = [round(x, 1) for x in np.arange(0.6, 1.8, 0.3)]
    #thresHProm = [round(x, 1) for x in np.arange(0.3, 0.8, 0.1)]
    if hierarUtile:
        thresHDeact_vals = [round(x, 1) for x in np.arange(0.5, 0.8, 0.1)]
    else:
        thresHDeact_vals = [0.7]
    return filter1_vals, stepUp_vals, upZPD_vals, deact_vals, prom_coef_vals, thresHDeact_vals


def gen_conf_to_optimize(save_path="experimentation/optimize/multiconf/", main_act="KT6kc", ref_stud="0", hierarUtile=0):

    if ref_stud in ["2"]:
        hierarUtile = 1

    filter1_vals, stepUp_vals, upZPD_vals, deact_vals, prom_coef_vals, thresHDeact_vals = all_values_zpdes(hierarUtile)

    print filter1_vals
    print stepUp_vals
    print upZPD_vals
    print deact_vals
    print prom_coef_vals
    print thresHDeact_vals

    multi_confs = {
        "ZpdesSsbg": {
            "ZpdesSsb": {
                "filter1": filter1_vals,
                "stepUpdate": stepUp_vals,
                "upZPDval": upZPD_vals,
                "deactZPDval": deact_vals,
                "promote_coeff": prom_coef_vals,
                "thresHDeact": thresHDeact_vals
            }
        }
    }

    base_conf = func.load_json("ZPDES_base", "params_files/ZPDES")
    base_conf["graph"]["file_name"] = "graph_{}_{}".format(main_act, ref_stud)
    base_conf["graph"]["main_act"] = main_act

    base_conf["graph"].update(func.load_json(base_conf["graph"]["file_name"], base_conf["graph"]["path"]))
    print base_conf
    zpdes_confs = mp.multi_conf(base_conf=base_conf, multi_params=multi_confs, combine=1)

    #conf_ids = mp.generate_diff_config_id(zpdes_confs)
    #zpdes_confs = {conf_ids[x] : zpdes_confs[x] for x in range(len(zpdes_confs))}
    uid = str(uuid.uuid1())

    jstr = json.dumps(zpdes_confs)

    k_lib.config.datafile.create_directories([save_path])
    save_path = "{}{}_{}_all_confs.json".format(save_path, main_act, ref_stud)
    k_lib.functions.write_in_file(save_path, jstr)

    return zpdes_confs


def gen_xp_to_optimize(zpdes_confs, ref_xp="optimize", nb_stud=1000, nb_step=100, base_path_to_save="experimentation/data/"):
    studconf = func.load_json(params_file="stud_KT6kc", directory="params_files/studModel")
    stud = k_lib.student.KTstudent(params_file="stud_KT6kc", directory="params_files/studModel")

    wkgs = {}
    for ref, conf in zpdes_confs.items():
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
                                          population={"nb_students": nb_stud,
                                                      "model": "KT_student"})
    return xp


def gen_set_zpdes_confs(nb_group_per_xp=10, nb_conf_to_test=None, main_act="KT6kc", ref_stud="0"):
    all_confs_file_path = "experimentation/optimize/multiconf/"
    all_confs_file = "{}_{}_all_confs.json".format(main_act, ref_stud)

    if os.path.isfile(os.path.join(all_confs_file_path, all_confs_file)):
        all_zpdes_confs = k_lib.functions.load_json(all_confs_file, all_confs_file_path)
    else:
        all_zpdes_confs = gen_conf_to_optimize(all_confs_file_path, main_act, ref_stud)

    all_conf_ids = mp.generate_diff_config_id(all_zpdes_confs)
    nb_conf_to_test = nb_conf_to_test or len(all_zpdes_confs)

    set_zpdes_confs = []

    for i in range(nb_conf_to_test / nb_group_per_xp):
        if nb_group_per_xp <= len(all_zpdes_confs) - i * nb_group_per_xp:
            nb_conf = nb_group_per_xp
        else:
            nb_conf = nb_group_per_xp - len(all_zpdes_confs) - i * nb_group_per_xp

        first_conf = i * nb_group_per_xp
        last_conf = i * nb_group_per_xp + nb_conf

        zpdes_conf = all_zpdes_confs[first_conf:last_conf]
        # print "i %s nbconf %s, z %s" % (i, nb_conf,len(zpdes_conf))

        conf_ids = all_conf_ids[first_conf:last_conf]

        zpdes_conf = {conf_ids[x]: zpdes_conf[x] for x in range(len(zpdes_conf))}
        set_zpdes_confs.append(zpdes_conf)

    return set_zpdes_confs


def gen_stud_confs(nb_students=1000, perturbated=0, params_file="stud_KT6kc_0"):
    studconf = func.load_json(params_file, "params_files/studModel")
    if perturbated == 1:
        pass
    else:
        stud_confs = [copy.deepcopy(studconf) for x in range(nb_students)]

    return stud_confs


def xp_conf_to_job(zpdes_conf, stud_confs, nb_step=100, studFile=""):
    xp_conf = {}
    xp_conf["zpdes_conf"] = zpdes_conf
    xp_conf["stud_confs"] = stud_confs
    xp_conf["nb_steps"] = nb_step
    xp_conf["stud_file"] = studFile

    return xp_conf


def full_optimize_zpdes(nb_group_per_xp=10, nb_stud=1000, nb_step=100, xp_type=0, nb_conf_to_test=None, ref_xp="KT6kc", ref_stud=0):
    stud_file = "stud_{}_{}".format(ref_xp, ref_stud)

    if xp_type == 1:
        jq = avakas_xp()
    else:
        jq = local_xp()

    kidleanrUrl = '-e git+https://github.com/flowersteam/kidlearn.git@origin/feature/xp_script#egg=kidlearn_lib'
    expeManageUrl = '-e git+https://github.com/wschuell/experiment_manager.git@origin/feature/ben_jobs#egg=experiment_manager'
    jrequirements = [expeManageUrl, kidleanrUrl]

    set_zpdes_conf = gen_set_zpdes_confs(nb_group_per_xp, nb_conf_to_test, main_act=ref_xp, ref_stud=ref_stud)

    for set_zpdes in set_zpdes_conf:
        stud_confs = gen_stud_confs(nb_students=nb_stud, params_file=stud_file)
        xp_conf = xp_conf_to_job(set_zpdes, stud_confs, nb_step=nb_step, studFile=stud_file)

        #file_to_save = xp.uuid+".dat"
        if xp_type == 1:
            jq.add_job(KidlearnJob(descr=jq.name, filename="data.dat", obj=xp_conf, step_fun="step_forward", steps=100, estimated_time=5400, virtual_env="test", requirements=jrequirements, path=jq.jobsdir, jq_path=jq.basedir))
        else:
            jq.add_job(KidlearnJob(descr=jq.name, filename="data.dat", obj=xp_conf, step_fun="step_forward", steps=100, estimated_time=3600, path=jq.jobsdir, jq_path=jq.basedir))

    if xp_type == 1:
        jq.check_virtualenvs()
        #xp_list.append(xp_to_job(first_conf=first_conf, last_conf=last_conf, zpdes_confs = zpdes_confs, conf_ids = conf_ids, nb_stud=nb_stud, nb_step=nb_step))

    return jq

def fit_exp_curve(xp):

    return


def cost_evol_conf(cost_mean, ref_conf):
    conf_dict_cost = []
    for key, val in cost_mean.items():
        conf_dict_cost.append(find_zpdes_conf(key, val))

    return conf_dict_cost


def find_zpdes_conf(confkey, cost=None):
    # for confkey,val in cost_mean.items():
    strconf = func.spe_split('_', confkey)[1]
    paramsconf = func.spe_split('[0-9]', strconf)
    valsconf = func.spe_split('[a-z]', strconf)
    values = {}
    for key, val in zip(paramsconf, valsconf):
        if int(val) > 100:
            val = val[1:]

        if key != "se":
            val = "{}.{}".format(val[0], val[1:])

        if val[0] == "0" and val[1] != ".":
            val = "{}.{}".format(val[0], val[1:])

        values[key] = float(val)

    if cost is not None:
        values["cost"] = cost

    return values

#########################################################
# Xp on Avakas
#########################################################
#########################################################


def perturbated_population(zpdes_confs, ref_xp="perturbation", nb_step=100, base_path_to_save="experimentation/data/"):
    population_conf = func.load_json(params_file="perturbation_KT6kc", directory="params_files/studModel")
    population = k_lib.student.Population(params=population_conf)
    nb_stud = population.nb_students

    wkgs = {}
    for ref, conf in zpdes_confs.items():
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
                                          population={"nb_students": nb_stud,
                                                      "model": "KT_student"})
    return xp


def calcul_cost_zpdes(zpdes_param, nb_stud=100, nb_step=100):
    print zpdes_param

    params = {
        "algo_name": "ZpdesHssbg",
        "graph": {
            "file_name": "KT6kc_graph",
            "path": "graph/",
            "main_act": "KT6kc"
        },
        "ZpdesSsbg": {
            "ZpdesSsb": {
                "filter1": zpdes_param[0],
                "filter2": 1 - zpdes_param[0],
                "uniformval": 0.05,
                "stepUpdate": int(zpdes_param[2]),
                "upZPDval": zpdes_param[3],
                "deactZPDval": zpdes_param[4],
                "promote_coeff": zpdes_param[5],
                "thresHProm": 0.3,
                "h_promote_coeff": 1,
                "thresZBegin": 0.4,
                "size_window": 3,
                "spe_promo": 0
            }
        }
    }

    stud = k_lib.student.KTstudent(params_file="stud_KT6kc", directory="params_files/studModel")
    zpdes = k_lib.seq_manager.ZpdesHssbg(params=params)
    ws_tab_zpdes = []
    for i in range(nb_stud):
        ws_tab_zpdes.append(k_lib.experimentation.WorkingSession(student=copy.deepcopy(stud), seq_manager=copy.deepcopy(zpdes)))
    wG_zpdes = k_lib.experimentation.WorkingGroup(WorkingSessions=ws_tab_zpdes)
    wG_zpdes.run(nb_step)
    print np.mean(wG_zpdes.calcul_cost())
    return np.mean(wG_zpdes.calcul_cost())


# example of complete simulation
def do_q_simu():
    simu = k_lib.experimentation.Experiment(params_file="simu_test_1")
    simu.run()

    for seq_name, group in simu._groups.items():

        data = group[0].get_ex_repartition_time(100)
        graph.kGraph.plot_cluster_lvl_sub([data], 100, 100,
                                          title="%s \nStudent distribution per erxercices type over time" % ("test"),
                                          path="simulation/graphics/",
                                          ref="clust_xseq_global_%s" % (seq_name),
                                          legend=["M1", "M2", "M3", "M4", "M5", "M6", "R1", "R2", "R3", "R4", "MM1", "MM2", "MM3", "MM4", "RM1", "RM2", "RM3", "RM4"],
                                          dataToUse=range(len([data])))


def change_graph_params(params, graph_file, main_act):
    params["graph"]["file_name"] = graph_file
    params["graph"]["main_act"] = main_act
    return params

# Xp with KT stud model, POMDP, ZPDES, Random %riarit%


def kt_expe(ref_xp="KT6kc", path_to_save="experimentation/data/", nb_step=100, nb_stud=100, files_to_load=None, ref_bis="", disruption_pop_file="perturbation_KT6kc", disruption=0, ref_pomdp="_2", ref_stud="_2", save_xp_data=0):
    if files_to_load is None:
        files_to_load = {}

    def_files_to_load = {}
    def_files_to_load["pomdp"] = {"file_name": "POMDP_{}{}".format(ref_xp, ref_pomdp), "path": "data/pomdp"}
    def_files_to_load["stud"] = "stud_{}{}".format(ref_xp, ref_stud)
    def_files_to_load["zpdes"] = "ZPDES_base"
    #def_files_to_load["riarit"] = "RIARIT_{}".format(ref_xp)
    def_files_to_load["random"] = "RANDOM_base"

    for key, val in def_files_to_load.items():
        if key not in files_to_load.keys():
            files_to_load[key] = val

    pomdP = k_lib.seq_manager.POMDP(load_p=files_to_load["pomdp"])

    #pomdP = k_lib.config.datafile.load_file("KT_expe_2","data/pomdp")

    zpdes_conf_opti = {}

    zpdes_params_0opti = {
        "algo_name": "ZpdesHssbg",
        "graph": {
            "file_name": "{}_graph".format(ref_xp),
            "path": "graph/",
            "main_act": "{}".format(ref_xp)
        },

        "ZpdesSsbg": {
            "ZpdesSsb": {
                "filter1": 0.2,  # 0.4,# 0.30,
                "uniformval": 0.05,  # 0.05,
                "stepUpdate": 4,  # 6,# 6,
                "upZPDval": 0.6,  # 0.6,
                "deactZPDval": 0.7,  # 0.4,# 0.5,
                "promote_coeff": 0.8,  # 1.7,
                "thresHProm": 0.5,  # 0.5,
                "h_promote_coeff": 0.25,  # 0.25,
                "size_window": 3,  # 3,
                "spe_promo": 0  # 0
            }
        }
    }

    zpdes_params_1opti = {
        "algo_name": "ZpdesHssbg",
        "graph": {
            "file_name": "{}_graph".format(ref_xp),
            "path": "graph/",
            "main_act": "{}".format(ref_xp)
        },

        "ZpdesSsbg": {
            "ZpdesSsb": {
                "filter1": 0.5,  # 0.4,# 0.30,
                "uniformval": 0.05,  # 0.05,
                "stepUpdate": 4,  # 6,# 6,
                "upZPDval": 0.7,  # 0.6,
                "deactZPDval": 0.6,  # 0.4,# 0.5,
                "promote_coeff": 0.6,  # 1.7,
                "thresHProm": 0.5,  # 0.5,
                "h_promote_coeff": 0.25,  # 0.25,
                "size_window": 3,  # 3,
                "spe_promo": 0  # 0
            }
        }
    }

    zpdes_params_2opti = {
        "algo_name": "ZpdesHssbg",
        "graph": {
            "file_name": "{}_graph".format(ref_xp),
            "path": "graph/",
            "main_act": "{}".format(ref_xp)
        },

        "ZpdesSsbg": {
            "ZpdesSsb": {
                "filter1": 0.1,  # 0.4,# 0.30,
                "uniformval": 0.05,  # 0.05,
                "stepUpdate": 4,  # 6,# 6,
                "upZPDval": 0.6,  # 0.6,
                "deactZPDval": 0.7,  # 0.4,# 0.5,
                "promote_coeff": 1.6,  # 1.7,
                "thresHProm": 0.5,  # 0.5,
                "h_promote_coeff": 0.25,  # 0.25,
                "size_window": 3,  # 3,
                "spe_promo": 0  # 0
            }
        }
    }

    zpdes_conf_opti["_0"] = zpdes_params_0opti
    zpdes_conf_opti["_1"] = zpdes_params_1opti
    zpdes_conf_opti["_2"] = zpdes_params_2opti

    #population_conf = func.load_json()
    population = k_lib.student.Population(params_file=disruption_pop_file, directory="params_files/studModel")
    #stud = k_lib.student.KTstudent(params=population.base_model)
    stud = k_lib.student.KTstudent(params_file=files_to_load["stud"], directory="params_files/studModel")
    nb_stud = nb_stud  # population.nb_students

    zpdes_params = func.load_json(file_name=files_to_load["zpdes"], dir_path="params_files/ZPDES")
    zpdes_params = change_graph_params(zpdes_params, "{}_graph".format(ref_xp), ref_xp)

    zpdes = k_lib.seq_manager.ZpdesHssbg(zpdes_params)  # params=zpdes_params)
    zpdesOpt = k_lib.seq_manager.ZpdesHssbg(zpdes_conf_opti[ref_pomdp])  # params=zpdes_params)
    #riarit = k_lib.seq_manager.RiaritHssbg(params_file=files_to_load["riarit"],directory="params_files/RIARIT")
    random_params = func.load_json(file_name=files_to_load["random"], dir_path="params_files/RANDOM")
    random_params = change_graph_params(random_params, "{}_graph".format(ref_xp), ref_xp)
    random = k_lib.seq_manager.RandomSequence(random_params)

    ws_tab_zpdes = []
    ws_tab_zpdesOpt = []
    #ws_tab_riarit = []
    ws_tab_random = []
    ws_tab_pomdp = []

    for i in range(nb_stud):
        if disruption == 1:
            stud = population.students[i]
        ws_tab_zpdes.append(k_lib.experimentation.WorkingSession(student=copy.deepcopy(stud), seq_manager=copy.deepcopy(zpdes)))
        ws_tab_zpdesOpt.append(k_lib.experimentation.WorkingSession(student=copy.deepcopy(stud), seq_manager=copy.deepcopy(zpdesOpt)))
        ws_tab_pomdp.append(k_lib.experimentation.WorkingSession(student=copy.deepcopy(stud), seq_manager=copy.deepcopy(pomdP)))
        #ws_tab_riarit.append(k_lib.experimentation.WorkingSession(student=copy.deepcopy(stud), seq_manager = copy.deepcopy(riarit)))
        ws_tab_random.append(k_lib.experimentation.WorkingSession(student=copy.deepcopy(stud), seq_manager=copy.deepcopy(random)))

    wG_zpdes = k_lib.experimentation.WorkingGroup(WorkingSessions=ws_tab_zpdes)
    wG_zpdesOpt = k_lib.experimentation.WorkingGroup(WorkingSessions=ws_tab_zpdesOpt)
    wG_pomdp = k_lib.experimentation.WorkingGroup(WorkingSessions=ws_tab_pomdp)
    #wG_riarit = k_lib.experimentation.WorkingGroup(WorkingSessions = ws_tab_riarit)
    #wG_random = k_lib.experimentation.WorkingGroup(WorkingSessions=ws_tab_random)

    wkgs = {
        "POMDP": [wG_pomdp],
        "ZPDES": [wG_zpdes],
        #"Random": [wG_random],
        "ZPDES2": [wG_zpdesOpt]
    }  # , "RIARIT": [wG_riarit]} # {"ZPDES": [wG_zpdes]} #

    ref_xp_bis = "{}{}".format(ref_xp, ref_bis)
    params = {
        "ref_expe": ref_xp_bis,
        "path_to_save": path_to_save,
        "seq_manager_list": wkgs.keys(),  # "RIARIT"
        "nb_step": nb_step,
        "population": {
            "nb_students": nb_stud,
            "model": "KT_student",
        }
    }

    xp = k_lib.experimentation.Experiment(WorkingGroups=wkgs, params=params)

    xp.run(nb_step)

    values_vect = ["V{}".format(i + 1) for i in range(len(xp.KC))]

    draw_xp_graph(xp, type_ex=values_vect, nb_ex_type=[1] * len(xp.KC))
    #all_mean_data = draw_xp_graph(xp,ref_xp)
    #cost = calcul_xp_cost(xp)

    if save_xp_data:
        xp.save()

    return xp


# all xp on same graph
def multi_kt_xp(ref_xp="KT6kc", path_to_save="experimentation/data/", nb_step=100, nb_stud=100, files_to_load=None, ref_bis="", disruption_pop_file="perturbation_KT6kc", disruption=0, refs_opti=["0", "1", "2", "3"], refs_stud=["0", "1", "2", "3"], save_xp_data=0, mixed_pop=1):

    if ref_bis == "" and disruption:
        ref_bis = "_dis_"

    if type(refs_stud) != list:
        refs_stud = [refs_stud]

    ref_bis = "{}opti{}_stud{}".format(ref_bis, "".join(refs_opti), "".join(refs_stud))
    if files_to_load is None:
        files_to_load = {}

    def_files_to_load = {}
    def_files_to_load["pomdp"] = []
    def_files_to_load["stud"] = []
    for ref in refs_opti:
        def_files_to_load["pomdp"].append({"file_name": "POMDP_{}_{}".format(ref_xp, ref), "path": "data/pomdp"})
    for ref in refs_stud:
        def_files_to_load["stud"].append("stud_{}_{}".format(ref_xp, ref))
    def_files_to_load["zpdes"] = "ZPDES_base"
    #def_files_to_load["riarit"] = "RIARIT_{}".format(ref_xp)
    def_files_to_load["random"] = "RANDOM_base"

    for key, val in def_files_to_load.items():
        if key not in files_to_load.keys():
            files_to_load[key] = val

    #pomdP = k_lib.config.datafile.load_file("KT_expe_2","data/pomdp")

    zpdes_conf_opti = {}
    zpdes_params_opti = {
        "0": [0.2, 0.05, 4, 0.6, 0.7, 0.8, 0.5, 0.5],
        "1": [0.1, 0.05, 4, 0.7, 0.6, 0.8, 0.5, 0.5],
        "2": [0.5, 0.05, 4, 0.8, 0.7, 1.5, 0.5, 0.5],
        "3": [0.4, 0.05, 4, 0.8, 0.6, 1.2, 0.5, 0.5],
        "4": [0.4, 0.05, 4, 0.8, 0.6, 1.2, 0.5, 0.5],
    }

    for ref in refs_opti:
        zpdes_conf_opti[ref] = {
            "algo_name": "ZpdesHssbg",
            "graph": {
                "file_name": "graph_{}_{}".format(ref_xp, ref),
                "path": "graph/",
                "main_act": "{}".format(ref_xp)
            },

            "ZpdesSsbg": {
                "ZpdesSsb": {
                    "filter1": zpdes_params_opti[ref][0],  # 0.4,# 0.30,
                    "uniformval": zpdes_params_opti[ref][1],  # 0.05,
                    "stepUpdate": zpdes_params_opti[ref][2],  # 4,# 6,
                    "upZPDval": zpdes_params_opti[ref][3],  # 0.6,
                    "deactZPDval": zpdes_params_opti[ref][4],  # 0.4,# 0.5,
                    "promote_coeff": zpdes_params_opti[ref][5],  # 1.7,
                    "thresHProm": zpdes_params_opti[ref][6],  # 0.5,
                    "thresHDeact": zpdes_params_opti[ref][7]
                }
            }
        }

    params_pop = []
    for ref in refs_stud:
        p_pop = func.load_json("{}_{}".format(disruption_pop_file, ref), "params_files/studModel")
        p_pop["nb_students"] = nb_stud
        params_pop.append(p_pop)
    if disruption == 1:
        population = k_lib.student.Population(params=params_pop)
    elif mixed_pop:
        stud_list = []
        for ii in range(len(refs_stud)):
            for i in range(nb_stud):
                stud_list.append(k_lib.student.KTstudent(params_file=files_to_load["stud"][ii], directory="params_files/studModel"))
        population = k_lib.student.Population(stud_list=stud_list)

    else:
        stud_list = {}
        for ii in range(len(refs_stud)):
            stud_list[refs_stud[ii]] = []
            for i in range(nb_stud):
                stud_list[refs_stud[ii]].append(k_lib.student.KTstudent(params_file=files_to_load["stud"][ii], directory="params_files/studModel"))
        population = k_lib.student.Population(stud_list=stud_list)

    #stud = k_lib.student.KTstudent(params=population.base_model)
    # nb_stud = nb_stud  # population.nb_students

    pomdPs = []
    zpdesOpts = []
    zpdesHs = []

    zpdes_params = func.load_json(file_name=files_to_load["zpdes"], dir_path="params_files/ZPDES")

    # zpdesH = k_lib.seq_manager.ZpdesHssbg(zpdes_params)  # params=zpdes_params)

    for i in range(len(refs_opti)):
        pomdPs.append(k_lib.seq_manager.POMDP(load_p=files_to_load["pomdp"][i]))
        zpdesOpts.append(k_lib.seq_manager.ZpdesHssbg(zpdes_conf_opti[refs_opti[i]]))  # params=zpdes_params)

        zpdes_params = change_graph_params(zpdes_params, "graph_{}_{}".format(ref_xp, refs_opti[i]), ref_xp)
        zpdesHs.append(k_lib.seq_manager.ZpdesHssbg(zpdes_params))
    #riarit = k_lib.seq_manager.RiaritHssbg(params_file=files_to_load["riarit"],directory="params_files/RIARIT")
    random_params = func.load_json(file_name=files_to_load["random"], dir_path="params_files/RANDOM")
    random_params = change_graph_params(random_params, "graph_{}_{}".format(ref_xp, refs_opti[i]), ref_xp)
    random = k_lib.seq_manager.RandomSequence(random_params)

    ws_tab_zpdes = [[] for i in range(len(refs_opti))]
    ws_tab_zpdesOpt = [[] for i in range(len(refs_opti))]
    ws_tab_pomdp = [[] for i in range(len(refs_opti))]
    #ws_tab_riarit = []
    ws_tab_random = []

    for i in range(len(population.students)):
        stud = population.students[i]
        for ii in range(len(refs_opti)):
            ws_tab_zpdes[ii].append(k_lib.experimentation.WorkingSession(student=cPickle.loads(cPickle.dumps(stud, -1)), seq_manager=cPickle.loads(cPickle.dumps(zpdesHs[ii], -1))))
            ws_tab_zpdesOpt[ii].append(k_lib.experimentation.WorkingSession(student=cPickle.loads(cPickle.dumps(stud, -1)), seq_manager=cPickle.loads(cPickle.dumps(zpdesOpts[ii], -1))))
            ws_tab_pomdp[ii].append(k_lib.experimentation.WorkingSession(student=cPickle.loads(cPickle.dumps(stud, -1)), seq_manager=cPickle.loads(cPickle.dumps(pomdPs[ii], -1))))
        #ws_tab_riarit.append(k_lib.experimentation.WorkingSession(student=copy.deepcopy(stud), seq_manager = copy.deepcopy(riarit)))
        ws_tab_random.append(k_lib.experimentation.WorkingSession(student=copy.deepcopy(stud), seq_manager=copy.deepcopy(random)))

    wG_zpdes = [k_lib.experimentation.WorkingGroup(WorkingSessions=x) for x in ws_tab_zpdes]

    wG_zpdes2 = [k_lib.experimentation.WorkingGroup(WorkingSessions=x) for x in ws_tab_zpdesOpt]
    wG_pomdp = [k_lib.experimentation.WorkingGroup(WorkingSessions=x) for x in ws_tab_pomdp]
    #wG_riarit = k_lib.experimentation.WorkingGroup(WorkingSessions = ws_tab_riarit)
    wG_random = k_lib.experimentation.WorkingGroup(WorkingSessions=ws_tab_random)

    wkgs = {
        "POMDP": wG_pomdp,
        "ZpdesH": wG_zpdes,
        "Zpdes*": wG_zpdes2,
    }
    if len(refs_stud) == 1:
        wkgs["Random"] = [wG_random]
    # , "RIARIT": [wG_riarit]} # {"ZPDES": [wG_zpdes]} #

    ref_xp_bis = "{}{}".format(ref_xp, ref_bis)
    params = {
        "ref_expe": ref_xp_bis,
        "path_to_save": path_to_save,
        "seq_manager_list": wkgs.keys(),  # "RIARIT"
        "nb_step": nb_step,
        "population": {
            "nb_students": nb_stud * len(refs_stud),
            "model": "KT_student",
            "ref_stud": "stud_{}_{}".format(ref_xp, "".join(refs_stud))
        }
    }

    xp = k_lib.experimentation.Experiment(WorkingGroups=wkgs, params=params, unique_save=False)

    xp.run(nb_step)

    ref_sub_group = [copy.deepcopy(refs_opti)]
    #draw_xp_kc_curve(xp, ref_sub_group=ref_sub_group, subgroup_treat=True)
    #draw_xp_kc_curve(xp)

    values_vect = ["V{}".format(i + 1) for i in range(len(xp.KC))]
    # draw_xp_graph(xp, type_ex=values_vect, nb_ex_type=[1] * len(xp.KC), ref_sub_group=ref_sub_group)

    #draw_xp_histo(xp, type_ex=values_vect, nb_ex_type=[1] * len(xp.KC),)

    #pvals = calcul_pvals(xp)

    #draw_pvals(xp, pvals)
    #all_mean_data = draw_xp_graph(xp,ref_xp)
    #cost = calcul_xp_cost(xp)

    if save_xp_data:
        xp.save()

    return xp

# Expe to tune ZPDES


def expe_zpdes_promot(ref_xp="kt_multiZ", path_to_save="experimentation/data/", nb_step=100, nb_stud=100):
    zpdes_confs = mp.multi_conf("multi_conf_test", "ZPDES_KT6kc", "params_files/ZPDES", combine=1)

    stud = k_lib.student.KTstudent(params_file="stud_KT6kc", directory="params_files/studModel")

    zpdes_confs = {mp.generate_diff_config_id(zpdes_confs)[x]: zpdes_confs[x] for x in range(len(zpdes_confs))}

    wkgs = {}
    for ref, conf in zpdes_confs.items():
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
                                          population={"nb_students": nb_stud,
                                                      "model": "KT_student"})
    xp.run()
    xp.save()
    draw_xp_graph(xp, ["V1", "V2", "V3", "V4", "V5", "V6"], nb_ex_type=[1, 1, 1, 1, 1, 1])

    return xp


def draw_xp_histo(xp, type_ex=["V1", "V2", "V3", "V4", "V5"], nb_ex_type=[1, 1, 1, 1, 1]):
    # draw histo graph to visualise exercise in time
    for seq_name, group in xp._groups.items():
        for i in range(len(group)):
            seq_name_title = seq_name.replace("*", "E")
            data = group[i].get_ex_repartition_time(first_ex=1, nb_ex=xp.nb_step + 1, main_rt=xp.main_act, type_ex=type_ex, nb_ex_type=nb_ex_type)
            graph.kGraph.plot_cluster_lvl_sub([data], xp.nb_students, xp.nb_step, title="%s_%s \nStudent distribution per erxercices type over time" % (seq_name, i), path="%s" % (xp.save_path), ref="exTime_%s_%s_%s" % (xp.ref_expe, seq_name_title, i), legend=type_ex, dataToUse=range(len([data])), show=0)


def draw_xp_kc_curve(xp, ref_sub_group=None, subgroup_treat=False, showPlot=False, use_std=False):
    # draw learning curve

    skill_labels = ["All"]
    kc_data = xp.get_kc_mean_std(subgroup_treat=subgroup_treat)
    labels = []
    seq_names = xp._groups.keys()
    colors = [["#00BBBB"], ["red"], ["black"]]

    if "Random" in seq_names:
        colors = [["#00BBBB"], ['purple'], ["red"], ["black"]]

    for seq_name, iii in zip(seq_names, range(len(xp._groups.keys()))):
        if ref_sub_group is not None and subgroup_treat is True and seq_name != "Random":
            labels.append(["%s_%s" % (seq_name, x) for x in ref_sub_group])
        else:
            labels.append([seq_name])

    for kc in range(len(kc_data)):
        mean_data = kc_data[kc]["mean"]
        std_data = None
        if use_std:
            std_data = kc_data[kc]["std"]

        graph.kGraph.draw_curve(mean_data, labels=labels, nb_ex=xp.nb_step + 1, typeData="Average KC level", type_data_spe="", ref="%s_%s_sg%s" % (xp.ref_expe, skill_labels[kc], int(subgroup_treat)), markers=None, colors=colors, line_type=['solid', 'dashed', 'dashdot', "dotted"], legend_position=5, path="%s" % (xp.save_path), showPlot=showPlot, std_data=std_data)
    return


def draw_pvals(xp, pvals):
    pv = []
    pvlabel = []
    for key, val in pvals.items():
        pv.append(val)
        pvlabel.append(key)
    graph.kGraph.draw_curve([pv], labels=[pvlabel], nb_ex=xp.nb_step, typeData="p_values_skill", type_data_spe="", ref="%s_%s" % (xp.ref_expe, "All"), markers=None, colors=[["#00BBBB", "green", "black", '#FF0000', '#FF6600', '#FF0066']], line_type=['dashed', 'dashdot', 'solid', "dotted", 'dashed', 'solid'], legend_position=5, std_data=None, path="%s" % (xp.save_path), showPlot=False)


def calcul_pvals(xp, steps=None, max_pvals=1, save_vals=False):
    skill_labels = xp.KC
    skill_labels.append("All")
    k = len(skill_labels) - 1
    all_data = {}
    for seq_name, group in xp._groups.items():
        all_data[seq_name] = []
        for subgroup in group:
            all_data[seq_name] += [subgroup.get_students_level(time=x, kc=k) for x in range(xp.nb_step)]
        # print data
        # raw_input()

    all_pvals = {}

    for data in itertools.combinations(all_data.iteritems(), 2):
        pvals = []
        for i in range(1, xp.nb_step):
            if steps is None:
                pvals.append(min(max_pvals, sstats.f_oneway(data[0][1][i], data[1][1][i])[1]))
            elif i in steps:
                pvals.append(min(max_pvals, sstats.f_oneway(data[0][1][i], data[1][1][i])[1]))
        all_pvals["{}/{}".format(data[0][0], data[1][0])] = pvals

    if save_vals:
        file_path = "{}pvals".format(xp.save_path)
        func.write_in_file(file_path, json.dumps(all_pvals))

    return all_pvals


# Statitical significance
def kruskal(dataToAnov):
    HVal, pVal = sstats.kruskal(*dataToAnov)
    return pVal

# Script to draw xp graphs


def draw_xp_graph(xp, type_ex, nb_ex_type, ref_sub_group=None):
    draw_xp_histo(xp, type_ex, nb_ex_type)
    draw_xp_kc_curve(xp, ref_sub_group)

    return

#############################################################################
# Cost
#############################################################################


def recup_mean_cost_from_jq(jq=None, jq_uuid=None):
    jq_uuid = jq_uuid or jq.uuid
    allcost_name = "jq/" + jq_uuid + "/all_cost_" + jq_uuid
    allcost = k_lib.func.load_json(allcost_name)
    nc = calcul_xp_cost(cost=allcost)
    cost_mean = copy.deepcopy(nc["mean"])

    return cost_mean


# calcul xp costs
def calcul_xp_cost(xp=None, cost=None):
    # calcul cost for each student
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
        json.dump(data_cost, outfile)

    return data_cost


def find_opti_conf(cost_mean):

    max_val_key = []
    for key, val in cost_mean.items():
        if val == max(cost_mean.values()):
            max_val_key.append(key)

    return max_val_key


def curve_cost_evolv(cost_mean):
    filter1_vals, stepUp_vals, upZPD_vals, deact_vals, prom_coef_vals = all_values_zpdes()

    #dict_cost_conf = {}
    opti_conf_key = find_opti_conf(cost_mean)[0]

    opti_conf = find_zpdes_conf(opti_conf_key)  # ,cost=cost_mean[opti_conf_key])

    val_tab_to_curve = {}

    for key in opti_conf.keys():
        val_tab_to_curve[key] = []
        for confkey, cost in cost_mean.items():
            conf = find_zpdes_conf(confkey)  # ,cost=cost)
            equal = 0
            for key2 in opti_conf.keys():
                # print "key {} key2 {}".format(key,key2)
                if key2 != key and conf[key2] == opti_conf[key2]:
                    equal += 1
            if equal == len(opti_conf.keys()) - 1:
                val_tab_to_curve[key].append((conf[key], cost))
        val_tab_to_curve[key].sort()
    return val_tab_to_curve


def curve_cost_val_compare_conf(conf_val):
    for key, val in conf_val.items():
        plt.cla()
        plt.clf()
        print key
        plt.close()
        plt.plot([valu[0] for valu in val], [valu[1] for valu in val])
        plt.show()


def gen_all_pomdp():
    pomdp_model_base = k_lib.func.load_json("POMDP_KT6kc", "params_files/POMDP")
    for nbKc in [10]:  # 2,3,4,5,7,
        print nbKc
        pomdp_model = copy.deepcopy(pomdp_model_base)
        pomdp_model["ref"] = "KT{}kc_0".format(nbKc)
        pomdp_model["actions"] = "KT{}kc".format(nbKc)
        pomdp_model["n_Action"] = nbKc
        pomdp_model["learn_model"]["file_name"] = "stud_KT{}kc_0".format(nbKc)
        path = "params_files/POMDP/POMDP_KT{}kc.json".format(nbKc)
        func.write_in_file(path, json.dumps(pomdp_model))
        k_lib.seq_manager.POMDP(params=pomdp_model, save_pomdp=1)


##########################################
# Stats
##########################################

def orgaTestDiffData(dTest1, dTest2):
    dT1 = [[] for x in range(len(dTest1[0]))]
    dT2 = [[] for x in range(len(dTest2[0]))]

    for al in dTest1:
        for tData in range(len(al)):
            for stud in al[tData]:
                dT1[tData].append(stud)

    for al in dTest2:
        for tData in range(len(al)):
            for stud in al[tData]:
                dT2[tData].append(stud)

    return [dT1, dT2]


def chi2AllErrorTrans(allErrorTrans, axis=0):  # /!\ not good chi2 funtion
    nbGroup = len(allErrorTrans)
    nbEx = len(allErrorTrans[0])

    chi2Xval = []
    chi2Pval = []

    for j in range(nbEx):
        obs = []
        for i in range(nbGroup):
            obs.append(allErrorTrans[i][j])
        obs = np.array(obs).T
        obs.shape
        #################################################
        Xval, Pval = sstats.chisquare(obs, axis=axis)
        #################################################
        chi2Xval.append(Xval)
        chi2Pval.append(Pval)

    return chi2Pval


def anovaPaperEx(data, paramToAnalyse=8):
    dataToAnov = []
    for al in data:
        alData = []
        for stud in al[paramToAnalyse]:
            alData.append(stud)
        dataToAnov.append(alData)

    fVal, pVal = sstats.f_oneway(*dataToAnove)
    print "f : %s, p : %s" % (fVal, pVal)
    HVal, pVal = sstats.kruskal(*dataToAnov)
    print "H : %s, p : %s" % (fVal, pVal)

    return


def savemat(mat):
    x = np.linspace(0, 2 * np.pi, 100)
    y = np.cos(x)

    scipy.io.savemat('test.mat', dict(x=x, y=y))

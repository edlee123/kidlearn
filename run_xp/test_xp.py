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
import run_xp
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

from kidlearn_lib.config import manage_param as mp
from kidlearn_lib import functions as func
from experiment_manager.job_queue import get_jobqueue
from experiment_manager.job.kidlearn_job import KidlearnJob
from experiment_manager.job.classic_job import ClassicJob
import matplotlib.pyplot as plt
import matplotlib.cm as cm

sys.path.append("../..")
import plot_graphics as graph


def test_new_zpdes(ref_xp="KT6kc", path_to_save="experimentation/data/", nb_step=100, nb_stud=100, files_to_load=None, ref_bis="test", disruption_pop_file="perturbation_KT6kc", disruption=0, ref_pomdp="2", ref_stud="2", save_xp_data=0):
    params_zpdes = {
        "algo_name": "ZpdesHssbg",
        "graph": {
            "file_name": "graph_KT6kc_2",
            "path": "graph/",
            "main_act": "KT6kc"
        },

        "ZpdesSsbg": {
            "ZpdesSsb": {
                "filter1": 0.20,
                "uniformval": 0.05,
                "stepUpdate": 6,
                "upZPDval": 0.5,
                "deactZPDval": 0.7,
                "promote_coeff": 1,
                "thresHierarProm": 0.1,
                "h_promote_coeff": 0.5,
                "size_window": 3,
                "spe_promo": 0
            }
        }
    }

    #population = k_lib.student.Population(params=params_pop)
    #stud = k_lib.student.KTstudent(params=population.base_model)
    stud_file = "stud_{}_{}".format(ref_xp, ref_stud)
    stud = k_lib.student.KTstudent(params_file=stud_file, directory="params_files/studModel")
    zpdes = k_lib.seq_manager.ZpdesHssbg(params=params_zpdes)
    ws_tab_zpdes = []
    for i in range(100):
        ws_tab_zpdes.append(k_lib.experimentation.WorkingSession(student=copy.deepcopy(stud), seq_manager=copy.deepcopy(zpdes)))

    wG_zpdes = k_lib.experimentation.WorkingGroup(WorkingSessions=ws_tab_zpdes)
    wkgs = {
        "ZPDES": [wG_zpdes],
    }

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

    run_xp.draw_xp_graph(xp, type_ex=values_vect, nb_ex_type=[1] * len(xp.KC))

    return xp

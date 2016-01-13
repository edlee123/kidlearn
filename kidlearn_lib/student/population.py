#-*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        KTstudent
# Purpose:
#
# Author:      Bclement
#
# Created:     14-03-2015
# Copyright:   (c) BClement 2015
# Licence:     GNU Affero General Public License v3.0

#-------------------------------------------------------------------------------
import numpy as np
import uuid
import copy

from .kt_student import KTstudent
from .. import functions as func


################################################################################
# Class Population
################################################################################

class Population(object):

    def __init__(self, params=None, params_file=None, directory="params_files", *args, **kwargs):
        if params is not None or params_file is not None:
            params = params or func.load_json(params_file, directory)
        self.params = params
        self.uuid = str(uuid.uuid1())
        self.base_model = params["base_model"]
        self.disrupted_models = params["disrupted_model"]
        self.nb_students = params["nb_students"]
        self.students_models = []
        self.students = []
        self.perturb_KT_model()

    def perturb_KT_model(self):
        trans_dep_mv = self.disrupted_models["kc_trans_dep"]
        trans_dep_pert = []
        for i in range(len(self.base_model["kc_trans_dep"])):
            mean = trans_dep_mv["mean"][i]
            cov = np.diag(trans_dep_mv["var"][i])
            trans_dep_pert.append(np.array(np.random.multivariate_normal(mean, cov, self.nb_students)))

        kt_mv = self.disrupted_models["KT"]
        kt_pert = {}
        for key in self.base_model["KT"].keys():
            mean = kt_mv["mean"][key]
            cov = np.diag(kt_mv["var"][key])
            kt_pert[key] = np.array(np.random.multivariate_normal(mean, cov, self.nb_students))
            for i in range(len(kt_pert[key])):
                for j in range(len(kt_pert[key][i])):
                    if kt_pert[key][i][j] < 0:
                        kt_pert[key][i][j] = 0.01

        for i in range(self.nb_students):
            new_model = copy.deepcopy(self.base_model)
            for x in range(len(trans_dep_pert)):
                new_model["kc_trans_dep"][x] = np.array(new_model["kc_trans_dep"][x]) - trans_dep_pert[x][i]
                new_model["kc_trans_dep"][x] = [max(new_model["kc_trans_dep"][x][y], 0.01) for y in range(len(new_model["kc_trans_dep"][x]))]

            for key in self.base_model["KT"].keys():
                new_model["KT"][key] = np.array(new_model["KT"][key]) - kt_pert[key][i]
            self.students_models.append(new_model)
            self.students.append(KTstudent(params=new_model))

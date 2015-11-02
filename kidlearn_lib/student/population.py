#-*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        KTstudent
#Purpose:
#
# Author:      Bclement
#
# Created:     14-03-2015
# Copyright:   (c) BClement 2015
# Licence:     GNU Affero General Public License v3.0

#-------------------------------------------------------------------------------
import numpy as np
import scipy.stats as sstats
import uuid
import copy

from .student import Student
from .. import functions as func


################################################################################
## Class Population
################################################################################

class Population(object):

    def __init__(self,params = None, params_file = None, directory = "params_files", *args, **kwargs):
        if params != None or params_file != None: 
            params = params or func.load_json(params_file,directory)

        self.uuid = str(uuid.uuid1())
        self.base_model = params["base_model"]
        self.perturbated_models = params["base_model"]
        self.nb_students = params["nb_students"]
        self.students_models = []


    def perturbate_KT_model(self):
        trans_dep_mv = perturbated_models["kc_trans_dep"]
        trans_dep_pert = []
        for i in range(len(self.base_model["kc_trans_dep"])):
            mean = trans_dep_mv["mean"][i]
            cov = np.diag(trans_dep_mv["var"][i])
            trans_dep_pert.append(np.array(np.random.multivariate_normal(mean,cov,self.nb_students)))

        kt_mv = perturbated_models["KT"]
        kt_pert = {}
        for key in self.base_model["KT"].keys():
            mean = kt_params["mean"][key]
            cov = np.diag(kt_params["var"][key])
            kt_pert[key] = np.array(np.random.multivariate_normal(mean,cov,self.nb_students))

        for i in range(self.nb_students):
            new_model = copy.deepcopy(self.base_model)
            for x in range(len(trans_dep_pert)):
                new_model["kc_trans_dep"][x] = np.array(new_model["kc_trans_dep"][x]) - trans_dep_pert[x][i]
            for key in self.base_model["KT"].keys():
                new_model["KT"][key] = np.array(new_model["KT"][key]) - kt_pert[key][i]
            self.students_models.append(new_model)




        
    def gen_population(self):
        pass

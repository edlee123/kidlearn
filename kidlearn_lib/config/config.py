#-*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        config
# Purpose:
#
# Author:      Bclement
#
# Created:     14-03-2015
# Copyright:   (c) BClement 2015
# Licence:     GNU Affero General Public License v3.0
#-------------------------------------------------------------------------------

from seq_manager import seq_dict_gen
#from exercise import *
from student import stud_dict_gen
from knowledge import *
from experimentation import *
import functions as func
import numpy as np
import copy as copy
import json
import os
import re

##############################################################
## ID config generations management
##############################################################

def code_id(strid,strval,nbCar = 1):
    return "{}{}{}".format(strid[:nbCar],strid[-nbCar:],strval)

def data_from_json(json,id_values = None,form = 0, ignore = ["name","path"]):
    if id_values is None:
        if form == 0:
            id_values= {}
        else:
            id_values = []
    for key,val in json.items():
        if key not in ignore:
            if isinstance(val,dict):
                data_from_json(val,id_values,form,ignore)
            else:
                if form == 0:
                    id_values[key] = val
                elif form == 1:
                    id_values.append(code_id(str(key),str(val)))
                elif form == 2:
                    id_values.append([str(key),str(val)])
    return id_values

def id_str_ftab(id_tab):
    idstr = ""
    for strValId in id_tab:
        idstr += strValId
    return idstr

def generate_diff_config_id(config_list):
    all_id = []
    for conf in config_list:
        all_id.append(data_from_json(conf,form =0))
    final_all_id = []
    for numConf in range(len(all_id)):
        nconf_id = []
        for key,val in all_id[numConf].items():
            valOK = 0
            for numConfb in range(len(all_id)):
                if numConf != numConfb and val != all_id[numConfb][key]:
                    valOK += 1
            if valOK > 0 :
                val = str(val)
                val = val.replace(".","")
                nconf_id.append(code_id(key,str(val)))
        nconf_id.sort()
        final_all_id.append(id_str_ftab(nconf_id))
    
    return final_all_id

##############################################################
## Multi Parameters For Algorithms
##############################################################

# Generate many parameters conf from base + file
def exhaustive_params(multi_param_file, base_param_file, directory):
    base_params = func.load_json(base_param_file,directory)
    multi_params = func.load_json(multi_param_file,directory)
    
    params_configs = [base_params]
    for paramKey,paramVal in multi_params.items():
        access_keys = []
        params_configs = gen_multi_conf(params_configs,paramKey,paramVal,access_keys)

    return params_configs

def gen_multi_conf(params_configs,paramKey,paramValue,access_keys):
    naccess_keys = copy.deepcopy(access_keys)
    naccess_keys.append(paramKey)
    if isinstance(paramValue,list):
        conf = copy.deepcopy(params_configs)
        for pconf in conf:
            nc = copy.deepcopy(pconf)
            for newParamVal in paramValue:
                nnc = copy.deepcopy(nc)
                access_dict_value(nnc,naccess_keys,newParamVal)
                params_configs.append(nnc)

    elif isinstance(paramValue,dict):
        for pkey,pval in paramValue.items():
            params_configs = gen_multi_conf(params_configs,pkey,pval,naccess_keys)

    return params_configs

# acces to json value or repalce
def access_dict_value(params,dict_keys, replace = None):
    if len(dict_keys) > 1 :
        return access_dict_value(params[dict_keys[0]],dict_keys[1:],replace)
    else:
        if replace != None:
            params[dict_keys[0]] = replace
        else:
            return params[dict_keys[0]]

##############################################################
## Define Objects from Modules
##############################################################

# Define sequence manager
##############################################################

def seq_manager(seq_params = None, params_file = None, directory = None):
    seq_params = seq_params or func.load_json(params_file,directory)
    seq_manager_name = seq_params["name"]

    return seq_dict_gen[seq_manager_name](seq_params)

# Define Student
##############################################################
def student(stud_params = None, params_file = None, directory = None):
    stud_params = stud_params or func.load_json(params_file,directory)
    model_student = stud_params["model"]

    return stud_dict_gen[model_student](stud_params)


##############################################################
## Population generation functions
##############################################################

""" TO DO AND UPGRADE """

# Generate population
##############################################################

def population(pop_params = None, params_file = None, directory = None):
    pop_dict_define = {}
    pop_dict_define["q_population"] = q_population

    pop_params = pop_params or func.load_json(params_file,directory)
    return pop_dict_define[pop_params["model"]](pop_params)


# Q population
##############################################################

def q_population(pop_params):
    nb_students = pop_params["nb_students"]
    mean = pop_params["mean"] 
    var = pop_params["var"]

    population_q_profiles = generate_q_profiles(nb_students,mean,var)
    population = []

    for stud_skills in population_q_profiles:
        params = pop_params["student"]
        params["knowledge_levels"] = stud_skills

        population.append(params)

    return population

def generate_q_profiles(nb_students,mean,var):
    
    population_q_profiles = generate_normal_population(nb_students,mean,var)
    for stud in population_q_profiles:
        stud = correct_skill_vector(stud)
    return population_q_profiles

# KT population
##############################################################

def kt_population(pop_params):
    nb_students = pop_params["nb_students"]
    mean = pop_params["mean"] 
    var = pop_params["var"]


def generate_p_profiles(nb_students,p_student_profiles):
    # To verify

    nb_class = len(p_student_profiles)
    nbStudClass = nb_students/nb_class
    population_p_profiles = []
    for p in p_student_profiles:
        for i in range(0,nbStudClass):
            population_p_profiles.append(p)
    
    return population_p_profiles

# Population Generation Tools
##############################################################

def generate_normal_population(size_population, mean,var):
    cov = np.diag(var)
    population_normal = np.random.multivariate_normal(mean,cov,(size_population))
    #for i in range(0,len(lvl)) :
    #    print "%s max : %s min : %s" %(i, max(lvl[i]),min(lvl[i]))
    return population_normal


def correct_skill_vector(skill_vector):
    for i in [2,5]:
        if skill_vector[i] > skill_vector[i-1]:
            skill_vector[i] = skill_vector[i-1]
    for i in range(len(skill_vector)):
        if skill_vector[i] < 1 or skill_vector[i] > 1:
            skill_vector[i] = min(max(skill_vector[i],0),1)
        if i > 3: 
            if skill_vector[i] > skill_vector[i-3]:
                skill_vector[i] = skill_vector[i-1]
        skill_vector[i] = round(skill_vector[i],2)
    return skill_vector



# OLD
##############################################################
def generate_kt_parametrisation():
    return

def population_profiles(model_student, stud_params):
    if model_student == 0:
        population = generate_q_profiles(stud_params)

    elif model_student == 1:
        population = generate_pstudent(stud_params)

    elif model_student == 2:
        population = generate_ktstudent(stud_params)

    elif model_student == 3:
        population = generate_ktfeatures(stud_params)

    else:
        print "NOT GOOD STUD MODEL TYPE"

    return population

def generate_pstudent_population():
    population_p_profiles = generate_p_profiles()
    population_q_profiles = generate_q_profiles()
    population = []
    for i in range(nb_students):
        population.append(Pstudent(params = population_p_profiles[i], knowledge_levels = population_q_profiles[i], knowledge_names = knowledge_names))
    return population

def generate_ktstudent_population(kt_profil = 0):
    population = []
    for i in range(nb_students):
        population.append(KTStudent(knowledge_names = knowledge_names, knowledge_params = KTStudent_profils[kt_profil]))
    return population

def generate_ktfeatures_population(kt_profil = 0):
    population = []
    for i in range(nb_students):
        population.append(KTStudent(config._knowledges_conf))
    return population

    return population


#TO DO : 
#class Config(object):

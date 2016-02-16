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

import numpy as np
import copy
import json
import os
import re

from ..seq_manager import seq_dict_gen
from ..student import stud_dict_gen
from .. import functions as func

##############################################################
## Define Objects from Modules
##############################################################

# Define sequence manager
##############################################################

def seq_manager(seq_params = None, params_file = None, directory = None):
    if seq_params != None:
        if "file_name"in seq_params.keys():
            params_file = seq_params["file_name"]
            directory = seq_params["directory"]
    if params_file != None :
        seq_params = func.load_json(params_file,directory)
    seq_manager_name = seq_params["algo_name"]

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
    population_normal = np.random.multivariate_normal(mean,cov,size_population)
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
        population.append(KTstudent(knowledge_names = knowledge_names, knowledge_params = KTstudent_profils[kt_profil]))
    return population

def generate_ktfeatures_population(kt_profil = 0):
    population = []
    for i in range(nb_students):
        population.append(KTstudent(config._knowledges_conf))
    return population

    return population


#TO DO : 
#class Config(object):

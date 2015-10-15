#-*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        functions
# Purpose:
#
# Author:      Bclement
#
# Created:     14-03-2015
# Copyright:   (c) BClement 2015
# Licence:     GNU Affero General Public License v3.0
#-------------------------------------------------------------------------------

import re
import pickle
import json
import copy
import os
import sys 
import numpy as np
import scipy
import math

###############################################################################
# Math functions 
###############################################################################

def logistic_function(x, beta=10, alpha=0.6):
    y = 1.0/(1+math.exp(-beta*(x-alpha)))
    return y

###############################################################################
# JSON functions 
###############################################################################

def j_str_type(data):
    
    str_data = "\"%s\"" % str(data)
    return str_data

def j_couple(key, value, value_is_string):
    
    key = j_str_type(key)
    
    if value_is_string :
        value = j_str_type(value)        
    
    str_json = "%s: %s" % (key,str(value))
    return str_json

def j_col(data1, data2):
    
    str_json = "%s, %s" % (data1,data2)
    
    return str_json

def j_finish(str_json):
    
    str_json = "{%s}" % str_json
    return str_json
    
def j_col_many(datas):
    
    size = len(datas)
    str_json = datas[0]
    for i in range(1,size):
        str_json = j_col(str_json,datas[i])
    
    str_json = j_finish(str_json)
    
    return str_json

###############################################################################
# Files gestion functions 
###############################################################################

def generatePaths(directory="HSSBG_TEST1", main_directory="Simulation/", type_data="/data_simu_"):
    path_dir = main_directory + directory
    if not os.path.exists(path_dir):
        os.makedirs(path_dir)
        
    path_data = path_dir + type_data + directory + ".txt" 
    if path_dir[-1] != "/":
        path_dir += "/" + directory + "_"

    return path_dir,path_data

def write_in_file(path, stringToWrite, optionWrite="w"):
    with open(path,optionWrite) as fp:
        fp.write(stringToWrite)

def load_json(file_name, dir_path=""):
    file_name = file_name.split(".")[0] + ".json"
    path = os.path.join(dir_path,file_name)
    with open(path, 'rb') as fp:
        json_data = json.load(fp)

    return json_data

###############################################################################
# Auxiliary functions
###############################################################################

# RiARiT : function to let empty space in table declaration 
def fill_data(data, nb_data_expected):
    complete_data = data + [data[-1]]*(nb_data_expected-len(data))
    return complete_data

# Regex special slip
def spe_split(regex, line):
    tmp=re.split(regex,line)
    tmp = [x for x in tmp if x not in [None,'']]
    return tmp

# SSB function to sample bandit
def dissample(p):
    s = np.random.multinomial(1,p)
    return np.nonzero(s==1)[0][0]

# Default value for argument from dictionaries
def setattr_dic_or_default(obj, attrName, dic, defaultValue = 0):
    if dic is None: dic = {}
    if attrName in dic.keys():
        setattr(obj,attrName,dic[attrName])
    else:
        setattr(obj,attrName,defaultValue)
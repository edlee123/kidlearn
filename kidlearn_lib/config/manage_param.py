#-*- coding: utf-8 -*-
import numpy as np
import copy as copy
import json
import os
import re
from .. import functions as func

##############################################################
# General Param Loader
##############################################################


def load_param(file_name, directory):
    return param

##############################################################
# ID config generations management
##############################################################


def code_id(strid, strval, nbCar=1):
    nstrid = ""
    strid = [nstrid + x for x in func.spe_split("[0-9]", strid)][0]
    return "{}{}{}".format(strid[:nbCar], strid[-nbCar:], strval)


def data_from_json(json, id_values=None, form=0, ignore=["name", "path"]):
    if id_values is None:
        if form == 0:
            id_values = {}
        else:
            id_values = []
    for key, val in json.items():
        if key not in ignore:
            if isinstance(val, dict):
                data_from_json(val, id_values, form, ignore)
            else:
                if form == 0:
                    id_values[key] = val
                elif form == 1:
                    id_values.append(code_id(str(key), str(val)))
                elif form == 2:
                    id_values.append([str(key), str(val)])
    return id_values


def id_str_ftab(id_tab):
    idstr = ""
    for strValId in id_tab:
        idstr += strValId
    return idstr


def generate_diff_config_id(config_list, form=0):
    all_id = []
    for conf in config_list:
        all_id.append(data_from_json(conf, form=form))
    final_all_id = []
    for numConf in range(len(all_id)):
        nconf_id = []
        for key, val in all_id[numConf].items():
            valOK = 0
            for numConfb in range(len(all_id)):
                if numConf != numConfb and val != all_id[numConfb][key]:
                    valOK += 1
            if valOK > 0:
                val = str(val)
                val = val.replace(".", "")
                nconf_id.append(code_id(key, str(val)))
        nconf_id.sort()
        final_all_id.append(id_str_ftab(nconf_id))

    return final_all_id

##############################################################
# Multi Parameters For Algorithms And Load From Base file + some Param modified
##############################################################

# Generate many parameters conf from base + file


def multi_conf(multi_param_file=None, base_param_file=None, directory=None, combine=0, base_conf=None, multi_params=None, base_conf_in=1):
    base_conf = base_conf or func.load_json(base_param_file, directory)
    multi_params = multi_params or func.load_json(multi_param_file, directory)

    params_configs = [base_conf]
    for paramKey, paramVal in multi_params.items():
        access_keys = []
        params_configs = gen_multi_conf(params_configs, paramKey, paramVal, access_keys, combine)

    if base_conf_in == 0:
        del params_configs[0]

    return params_configs

# gen multi conf with combinaison or not


def gen_multi_conf(params_configs, paramKey, paramValue, access_keys, combine=0):
    naccess_keys = copy.deepcopy(access_keys)
    naccess_keys.append(paramKey)
    if isinstance(paramValue, list):
        if combine == 1:
            conf = copy.deepcopy(params_configs)
            for pconf in conf:
                nc = copy.deepcopy(pconf)
                for newParamVal in paramValue:
                    nnc = copy.deepcopy(nc)
                    func.access_dict_value(nnc, naccess_keys, newParamVal)
                    if nnc not in params_configs:
                        params_configs.append(nnc)

        else:
            while len(params_configs) < len(paramValue) + 1:
                params_configs.append(copy.deepcopy(params_configs[0]))
            for i in range(len(paramValue)):
                if paramValue[i] is not None:
                    func.access_dict_value(params_configs[i + 1], naccess_keys, paramValue[i])

    elif isinstance(paramValue, dict):
        for pkey, pval in paramValue.items():
            params_configs = gen_multi_conf(params_configs, pkey, pval, naccess_keys, combine)

    return params_configs

##########################################################################
# Generate one config from base config + new param file


def gen_new_conf(base_param_file=None, new_param_file=None, directory=None, base_conf=None, new_params=None):

    config = base_conf or func.load_json(base_param_file, directory)
    new_params = new_params or func.load_json(new_param_file, directory)

    for paramKey, paramVal in new_params.items():
        access_keys = []
        config = change_conf(config, paramKey, paramVal, access_keys)
    return config


def change_conf(config, paramKey, paramValue, access_keys):
    naccess_keys = copy.deepcopy(access_keys)
    naccess_keys.append(paramKey)
    if isinstance(paramValue, dict):
        for pkey, pval in paramValue.items():
            config = change_conf(config, pkey, pval, naccess_keys)
    else:
        func.access_dict_value(config, naccess_keys, paramValue)

    return config

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
from operator import mul
import uuid

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
        self.students = []
        self.base_model = params["base_model"]

    def perturbate_KT_model(self, perturbation):
        
        
    def gen_population(self):
        pass

#-*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        student
# Purpose:
#
# Author:      Bclement
#
# Created:     14-03-2015
# Copyright:   (c) BClement 2015
# Licence:     CreativeCommon
#-------------------------------------------------------------------------------

from knowledge import *
from functions import *
import numpy as np

import os
import re
import pickle
import json
import copy

class Student(object):

    def __init__(self,id = "x"):
        self._id = id
        self._knowledges = []
        #self._skills = skills
        return

    def get_state(self, seq_values = None):
        student_state = {}
        student_state["id"] = self._id

        return student_state

    def answer(self,activity):
        return



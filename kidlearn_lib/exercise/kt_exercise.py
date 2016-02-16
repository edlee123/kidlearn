#-*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        exercise
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
import re

from ..knowledge import Knowledge
from .exercise import Exercise

class KTExercise(Exercise):
    
    def __init__(self, act, knowledge_levels=None, knowledge_names=None, 
            answer=None, nbMax_try=1, params=None, *args,**kwargs):
        Exercise.__init__(self,act, knowledge_levels, knowledge_names, 
            answer, nbMax_try, params, *args,**kwargs)

    def compute_act_lvl(self, act, RT = None, **kwargs):
        pass


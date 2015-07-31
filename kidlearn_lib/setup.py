#-*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        setup
# Purpose:
#
# Author:      Bclement
#
# Created:     14-03-2015
# Copyright:   (c) BClement 2015
# Licence:     GNU Affero General Public License v3.0

#-------------------------------------------------------------------------------

import numpy as np
import copy as copy
import json
import config
import os

import kidlearn_lib as k_lib
import graph_lib as graph


# example of WorkingSession : one student and one seqequance manager

def do_work_session():
    WorkingSession = k_lib.experimentation.WorkingSession(params_file = "worksess_test_1")
    

    return

# example of complete simulation
def do_simu():
    simu = k_lib.experimentation.Experimentation(params_file = "simu_test_1")
    simu.run()

    for seq_name,group in simu._groups.items():

        data = group[0].get_ex_repartition_time(100)
        graph.kGraph.plot_cluster_lvl_sub([data],100,100, title = "%s \nStudent distribution per erxercices type over time" % ("test"),path = "simulation/graphics/", ref = "clust_xseq_global_%s" % (seq_name),legend = ["M1","M2","M3","M4","M5","M6","R1","R2","R3","R4","MM1","MM2","MM3","MM4","RM1","RM2","RM3","RM4"],dataToUse = range(len([data])))

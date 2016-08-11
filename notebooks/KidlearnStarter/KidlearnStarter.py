# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------------
# Name:        script KidlearnStarter
# Purpose:     
#
# Author:      Bclement
#
# Created:     14-03-2015
# Copyright:   (c) BClement 2015
# Licence:     GNU Affero General Public License v3.0
# ------------------------------------------------------------------------------

##KidlearnStarter

import sys
import os
import numpy as np
import time

sys.path.append("../..")
sys.path.append("../../kidlearn_lib/")

##Presentation

# The Kidlearn library includes a set of algorithms designed to guide a pedagogical sequence of activities, these algorithms are implemented in the seq_manager module of the library (explained in another notebook). To define the different possible exercises, we use "R-Table" which are described in our articles. To test and use these algorithms, we defined student models, implemented in student module, which have some skills to learn through a didactic sequence managed by an algorithm.

# In this notebook, we will focus on the experimentation module, which permit to manage different level of simulation. The parameter files are located in the folder paramas_files/, and the using R-Tables in RT/.

import kidlearn_lib as k_lib
import graph_lib as graph

##The experimentation objects

# We will introduce the different objects involved in experimentation module. In this notebook we will only use the "Q" student model and the "N1" R-Table.

##Working session

# A Working session is defined by a student and a sequence manager. It will permit to manage the activity sequence for the student s with the algorithm A.

# Use of a simple example of a configuration
# We create a student based on the Q model.

s = k_lib.config.student(params_file="qstud", directory="params_files")

# We create a sequence manager, here it's RiARiT (you can also try ZPDES).

A = k_lib.config.seq_manager(params_file="RIARIT", directory="params_files")
# A = k_lib.config.seq_manager(params_file="ZPDES",directory="params_files")

# We create a working session based on the student and the algorithm.

workSession = k_lib.experimentation.WorkingSession(student=s, seq_manager=A)
# same thing if we directly load worksession.json file
# workSession2 = k_lib.experimentation.WorkingSession(params_file="worksession",directory="params_files")

# To run one step, you can use the "step_forward()" function.

workSession.step_forward()
# def step_forward(self):
# ex = self.new_exercise() <- the algorithm choose the activity to do
# self.student_answer(ex) <- student answer to the activity
# self.save_actual_step() <- save the activity
# self.update_manager(ex) <- update to choose the next activity

workSession.actual_step()  # what is the last exercise done

# To run a sequence with n activities we will use the run(n) function.

workSession.run(100)  # do 100 times step_forward()

workSession.step[0:10]  # shows the first 10 steps

# Use of 3 sequence managers (RiARiT, ZPDES, Random)

wsRiarit = k_lib.experimentation.WorkingSession(params_file="ws_expe_RiARiT")
wsZpdes = k_lib.experimentation.WorkingSession(params_file="ws_expe_ZPDES")
wsRandom = k_lib.experimentation.WorkingSession(params_file="ws_expe_Random")

wsRiarit.run(100)
wsZpdes.run(100)
wsRandom.run(100)

print "Skill level after 100 steps :"
print "Riarit %s " % [wsRiarit.step[-1].student["knowledges"][i].level for i in range(len(wsRiarit.KC))]
print "ZPDES : %s" % [wsZpdes.step[-1].student["knowledges"][i].level for i in range(len(wsZpdes.KC))]
print "Random : %s" % [wsRandom.step[-1].student["knowledges"][i].level for i in range(len(wsRandom.KC))]

##Experiment

# The goal of the Experiment object is to give a tool to follow and analyze data from a population of students using different sequences managers, for example to compare RiARiT, ZPDES with a random or predefined sequence.

xp = k_lib.experimentation.Experiment(params_file="experiment_expe")

xp.run(100)

for seq_name, group in xp._groups.items():
    data = group[0].get_ex_repartition_time(first_ex=1, nb_ex=101)

show = 1  # graphs are saved in "path", replace show = 0 to not see the graph,
graph.kGraph.plot_cluster_lvl_sub([data], 100, 100,
                                  title="%s \nStudent distribution per erxercices type over time" % (seq_name),
                                  path="experiments/graphics/", ref="clust_xseq_global_%s" % (seq_name),
                                  legend=["M1", "M2", "M3", "M4", "M5", "M6", "R1", "R2", "R3", "R4", "MM1", "MM2",
                                          "MM3", "MM4", "RM1", "RM2", "RM3", "RM4"], dataToUse=range(len([data])),
                                  show=show)


reload(graph)
skill_labels = ["KM", "ISum", "Isub", "ID", "DSum", "DSub", "DD", "All"]
for k in range(len(skill_labels)):
    mean_data = []
    std_data = []
    # for seq_name, group in xp._groups.items():
    #     data = [group[0].get_students_level(time=x, kc=k) for x in range(101)]
    mean_data.append([np.mean(data[x]) for x in range(len(data))])
    std_data.append([np.std(data[x]) for x in range(len(data))])

graph.kGraph.draw_curve([mean_data], labels=[xp._groups.keys()], nb_ex=len(data), typeData="skill_level",
                        type_data_spe=skill_labels[k], ref=skill_labels[k], markers=None,
                        colors=[["#00BBBB", "green", '#FF0000', "black"]],
                        line_type=['dashed', 'dashdot', 'solid', "dotted"], legend_position=3, std_data=[std_data])

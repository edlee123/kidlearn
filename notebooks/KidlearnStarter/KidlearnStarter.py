#-*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        script KidlearnStarter
# Purpose:     
#
# Author:      Bclement
#
# Created:     14-03-2015
# Copyright:   (c) BClement 2015
# Licence:     GNU Affero General Public License v3.0
#------------------------------------------------------------------------------

import sys
import os
sys.path.append("..")
sys.path.append("../kidlearn_lib/")

##Presentation

#The Kidlearn library includes a set of algorithms designed to guide a pedagogical sequence of activity, this algorithm are implemented in the ***seq_manager*** module of the library. To define the different possible exercises, we use **"R-Table"** which are describe in our articles. To test and use this algorithms, we defined student models, implemented in ***student*** module, which have some skills to learn through a didactic sequence managed by an algorithm. 

#For the notebooks, the parameter files are located in the folder **notebooks/paramas_files/notebook1/**, and the using R-Table in **notebooks/RT/**.

#In this notebook, we will focus on the ***experimentation*** module, wich permit to managed different level of simulation. 

import kidlearn_lib as k_lib

##Introducing the objects

#We will first introduce the different objects involved in ***experimentation***. For this notebook we will only use the "$Q$" student model and the "*test1*" R-Table.

###Working session

#A *Working session* is defined with a student and a sequence manager. It will permit to manage the activity sequence for the student **s** with the algorithm **A**.

#We create a student based on the $Q$ model.

s = k_lib.config.student(params_file="qstud",directory="params_files/notebook1")

# We create a sequence manager, here it's ***RiARiT***.

A = k_lib.config.seq_manager(params_file="RIARIT",directory="params_files/notebook1")

# We crate a working session base on the student and the algorithm.

workSession = k_lib.experimentation.Working_session(student=s,seq_manager=A)

# To run one step, you can use the "*step_forward()*" function. 

workSession.step_forward()
# def step_forward(self):
    # act = self._seq_manager.sample() <- the algorithm choose the activity to do
    # ex_skill_lvl = self._seq_manager.compute_act_lvl(act,"main",dict_form =1) <- evalution of the activity level 
    # self._current_ex = Exercise(act,ex_skill_lvl,self._KC) <- exercise to do
    # self._student.answer(self._current_ex) <- student answer to the activity
    # self.save_actual_step() <- save the activity
    # self._seq_manager.update(act,self._current_ex._answer) <- update to choose the next activity

workSession.actual_step() # what is the last exercise done

#***"act"*** present the parametrisation of the activity. *"N1"* is the name of the Table, and the vector "N1 : [0,0,0] " represent the values taken by the 3 didactic parameters. 

#***"student skill"*** present the level of the student ($ \in [0;1]$) for each skill (here : *S0, S1, S2*).

# To run a sequence with $n$ activities we will use the *run($n$)* function. 

workSession.run(100) # do 100 times step_forward()

workSession.step[0:10] # show the first 10 step

##### Use of  and 3 sequences managers (RiARiT, ZPDES, Random)

wsRiarit = k_lib.experimentation.Working_session(params_file="ws_expe_RiARiT")
wsZpdes = k_lib.experimentation.Working_session(params_file="ws_expe_ZPDES")
wsRandom = k_lib.experimentation.Working_session(params_file="ws_expe_Random")

wsRiarit.run(100)
wsZpdes.run(100)
wsRandom.run(100)

print "Skill level after 100 steps :"
print "Riarit %s " % [wsRiarit.step[-1].student["knowledges"][i].level for i in range(len(wsRiarit.KC))]
print "ZPDES : %s" % [wsZpdes.step[-1].student["knowledges"][i].level for i in range(len(wsZpdes.KC))]
print "Random : %s"  % [wsRandom.step[-1].student["knowledges"][i].level for i in range(len(wsRandom.KC))]
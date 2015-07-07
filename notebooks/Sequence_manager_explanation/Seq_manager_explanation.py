#-*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        script Seq_manager_explanation
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
sys.path.append("../..")
sys.path.append("../../kidlearn_lib/")

# #Presentation

# As presented in KidlearnStarter notebook, the Kidlearn library includes a set of algorithms that we develop to guide pedagogical activities. We introduce two different algorithms ZPDES that uses a simple graph of knowledge and RiARiT that includes a more complex student model. The details of the algorithms and the user studies are presented in the following paper: B. Clement, D. Roy, P.-Y. Oudeyer, M. Lopes, Multi-Armed Bandits for Intelligent Tutoring Systems, Journal of Educational Data Mining (JEDM), 2015 [(arXiv:1310.3174 [cs.AI])](http://arxiv.org/abs/1310.3174).

# This algorithms are implemented in the ***seq_manager*** module of the library, with some others sequence managers used to evaluate our agorithms. In this notebook, we will describe how the module works and how define the file needed to describe an activity.

import kidlearn_lib as k_lib

# #The sequence manager objects

# There is 4 differents sequence manager wich are define for now : 
# - RiARiT : an algorithms based on student skill estimation
# - ZPDES : an algorithm based on the success of the student
# - Sequence : a predefined sequence of activities (defined by an expert)
# - Random : a random sequence on all activities. 

# ## RiARiT : The Right Activity at the Right Time
# RiARiT use tables to define the relation between skills and activities. The tables have this form : 


##############################################################################
### Problem with Markdown
### Theorical table of realtion ###

#| group $H_x$               ||       Knowledge Components                 |||
#|:----------:|:-------------:|:---------------:|:--------:|:---------------:|
#| Parameters |  Values       |    $KC_1$       | $\ldots$ |      $KC_3$     |
#|            | $v_{x,1,1}$   | $q_{x,1,1,1}$   | $\ldots$ | $q_{x,1,1,1}$   |
#| $a_{x,1}$  | $v_{x,1,2}$   | $q_{x,1,1,2}$   | $\ldots$ | $q_{x,1,1,2}$   |
#|            |   $\vdots$    |     $\vdots$    | $\vdots$ |     $\vdots$    |
#|            | $v_{x,1,k_1}$ | $q_{x,1,1,k_1}$ | $\ldots$ | $q_{x,1,1,k_1}$ |
#[Table of relation][RTable]

###############################################################################

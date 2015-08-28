#-*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        experimentation
# Purpose:
#
# Author:      Bclement
#
# Created:     14-03-2015
# Copyright:   (c) BClement 2015
# Licence:     GNU Affero General Public License v3.0
#-------------------------------------------------------------------------------

import os
import sys
from seq_manager import Sequence, ZpdesHssbg, RiaritHssbg, RandomSequence, POMDP
from exercise import Exercise
from student import *
import functions as func
import numpy as np
import copy as copy
import json
import config
import graph_lib as graph
import config.datafile as datafile
import time

#########################################################
#########################################################
## class SessionStep

class SessionStep(object):
    """\
        SessionStep Definition
    """

    def __init__(self, student_state = {}, seq_manager_state = {}, exercise = None, *args, **kwargs):
        self.student = student_state
        self.seq_manager = seq_manager_state
        self.exercise = exercise

        for key, val in kwargs.iteritems():
            object.__setattr__(self, key, val)
    
    @property
    def act(self):
        return self.exercise.act

    @property
    def ex_answer(self):
        return self.exercise.answer
    
    def __repr__(self):
        return  "act : {}, student skill: {}".format(self.exercise, self.student["knowledges"])

    ###########################################################################
    ##### Data Analysis tools 
    def get_attr(self,attr,*arg,**kwargs):
        data = getattr(self,attr)
        if len(arg)>0:
            if isinstance(data,dict) :
                return data[arg[0]]
            else:
                data = getattr(data,arg[0])

        return data

    def base(self):
        return

    ##### Data Analysis tools 
    ###########################################################################

## class SessionStep
#########################################################


#########################################################
#########################################################
## class States_matrix

#class States_matrix(object):


## class States_matrix
#########################################################

#########################################################
#########################################################
## class WorkingSession

class WorkingSession(object):
    """TODO"""

    def __init__(self, params = None, params_file = None, directory = "params_files", student = None, seq_manager = None, *args, **kwargs):

        if params != None or params_file != None:
            params = params or func.load_json(params_file,directory)
        self.params = params

        self._student = student or config.student(self.params["student"])
        self._seq_manager = seq_manager or config.seq_manager(self.params["seq_manager"])

        self._KC = self._seq_manager.get_KC()
        
        self._step = []
        self._current_ex = None
        self.save_actual_step()
        #self.log = SessionLog

    @property
    def student(self):
        return self._student

    @property
    def step(self):
        return self._step

    @property
    def nb_step(self):
        return len(self._step)

    @property
    def seq_manager(self):
        return self._seq_manager

    @property
    def KC(self):
        return self._KC

    # methods

    def run(self, nb_ex):
        for i in range(nb_ex):
            self.step_forward()

    def step_forward(self):
        ex = self.new_exercise()
        self.student_answer(ex)
        self.save_actual_step(ex)
        #self.log.log(new_ex, student_answer)
        self.update_manager(ex)

    def new_exercise(self):
        act = self._seq_manager.sample()
        ex_skill_lvl = self._seq_manager.compute_act_lvl(act,"main",dict_form =1)
        self._current_ex = Exercise(act,ex_skill_lvl,self._KC)
        return self._current_ex

    def student_answer(self, ex, answer=None, nb_try=0):
        if answer:
            self._student.answer(ex, answer, nb_try=nb_try)
        else:
            self._student.answer(ex, nb_try=nb_try)
    
    def update_manager(self, ex):
        self._seq_manager.update(ex.act, ex._answer)

    # to delete

    def actual_step(self,ex = None):
        return SessionStep(copy.deepcopy(self._student.get_state()),copy.deepcopy(self._seq_manager.get_state()),copy.deepcopy(ex or self._current_ex))
        
    def save_actual_step(self,ex = None):
        self._step.append(self.actual_step(ex))

    ###########################################################################
    ##### Data Analysis tools 
    
    def student_level_time(self,time = 0, kc = 0):
        if isinstance(kc,list):
            return np.mean([self._step[time].student["knowledges"][k].level for k in kc])

        elif kc >= len(self._step[time].student["knowledges"]):
            return np.mean([self._step[time].student["knowledges"][k].level for k in range(len(self._step[time].student["knowledges"]))])
        else:
            return self._step[time].student["knowledges"][kc].level

    def base(self):
        return


    ##### Data Analysis tools 
    ###########################################################################

## class WorkingSession
#########################################################


#########################################################
#########################################################
## class WorkingGroup
class WorkingGroup(object):
    def __init__(self, params = None, params_file = None, directory = "params_files",population = None, WorkingSessions = None, *args, **kwargs):
        #params : 

        params = params or func.load_json(params_file,directory)
        self.params = params
        self.logs = {}

        if WorkingSessions:
            self._working_sessions = WorkingSessions

        else:
            population = population or config.population(params = params["population"])
            self._working_sessions = []
            for student_params in population:
                params = {"student": student_params, "seq_manager": self.params["seq_manager"]}
                self._working_sessions.append(WorkingSession(params = params))


    @property
    def working_sessions(self):
        return self._working_sessions

    @property
    def students(self):
        students = [ws.student for ws in self._working_sessions]
        return students
    

    def get_WorkingSession(self,num_stud = 0, id_stud = None):
        if id_stud:
            for ws in self._working_sessions:
                if ws.student.id == id_stud:
                    return ws

        return self._working_sessions[num_stud]

    def run(self,nb_ex):
        for ws in self._working_sessions:
            ws.run(nb_ex)
    
    def add_student(self,student,seq_manager):
        self._working_sessions.append(WorkingSession(student,seq_manager))

    ###########################################################################
    ##### Data Analysis tools 
    
    def get_students_level(self, time = 0, kc = 0):
        skill_level = []
        for ws in self._working_sessions:
            skill_level.append(ws.student_level_time(time,kc))
        return skill_level

    def get_data_time(self, time = 0, attr = None, *arg, **kwargs):
        data = []
        for ws in self._working_sessions:
            if attr:
                data.append(ws.step[time].get_attr(attr,*arg))
            else: 
                data.append(ws.step[time])
        return data
    
    def get_act_repartition_time(self,first_ex = 1, nb_ex=101, act = "MAIN",nb_act = 5):
        repart = [[0 for x in range(nb_act)]]
        for num_ex in range(first_ex,nb_ex):
            exs = self.get_data_time(num_ex,"exercise","_act")
            for j in range(len(exs)):
                repart[exs[j][act][0]][num_ex-first_ex][0] += 1

        return repart

    def get_ex_repartition_time(self,first_ex = 1, nb_ex=101, type_ex=["M","R","MM","RM"], 
                                nb_ex_type=[6,4,4,4], main_rt = "MAIN"):
        
        repart = [[] for x in range(len(type_ex))]
        for num_ex in range(first_ex,nb_ex):
            exs = self.get_data_time(num_ex,"exercise","_act")
            for nbType in range(len(type_ex)):
                repart[nbType].append([0 for i in range(nb_ex_type[nbType])])
                #print repart
            for j in range(len(exs)):
                if nb_ex_type[exs[j][main_rt][0]] == 1:
                    repart[exs[j][main_rt][0]][num_ex-first_ex][0] += 1
                else:
                    repart[exs[j][main_rt][0]][num_ex-first_ex][exs[j][type_ex[exs[j][main_rt][0]]][0]] += 1

        return repart

    ##### Data Analysis tools 
    ###########################################################################


## class WorkingGroup
#########################################################

#########################################################
#########################################################
## class Experiment

class Experiment(object):
    def __init__(self,params = None, params_file = None, directory = "params_files",
                 WorkingGroups = None, *args, **kwargs):
        # params : seq_manager_list, nb_stud, nb_step, model_stud, ref_simu

        #self.config = self.load_config()
        params = params or func.load_json(params_file,directory)
        self.params = params
        self.logs = {}

        self._seq_manager_list_name = self.params["seq_manager_list"]
        self._nb_step = self.params["nb_step"]

        self._nb_students = self.params["population"]["nb_students"]
        self._model_student = self.params["population"]["model"]
        
        if "path_to_save" not in self.params.keys():
            self.params["path_to_save"] = "experimentation/data/"

        self.do_simu_path(self.params["ref_expe"], path = self.params["path_to_save"])

        for key, val in kwargs.iteritems():
            object.__setattr__(self, key, val)
        
        if WorkingGroups:
            self._groups = WorkingGroups

        else:
            self._groups = {key: [] for key in self._seq_manager_list_name}
            self._population = config.population(self.params["population"])

            for seq_manager_name in self._seq_manager_list_name:
                params = self.params["WorkingGroup"]
                params["seq_manager"] = self.params["seq_managers"][seq_manager_name]
                params["population"] = self._population
                self.add_WorkingGroup(params)

        #self.population_simulation()
        #self.population = []
        #self.define_seq_manager()

    @property
    def groups(self):
        return self._groups

    @property
    def students(self):
        return {sname : groups.students for sname,groups in self._groups.items()}


    def load_config(self, params_file = None):
        
        return 

    def add_WorkingGroup(self,params):
        self._groups[params["seq_manager"]["name"]].append(WorkingGroup(params = params, population = self._population))
        #self._groups[seq_manager_name].append(WorkingGroup(population,self.define_seq_manager(seq_manager_name)))

    def do_simu_path(self,ref = "", directory = "", path = ""):
        for seqName in self._seq_manager_list_name:
            directory += "%s_" % seqName[0:min(len(seqName),2)]
        directory = "%sms%s" % (directory,self._model_student)
        self._directory = "%s/%s" % (path,directory) 
        self._ref_simu = "%s_ns%s_ne%s_%s" % (directory,self._nb_students,self._nb_step,ref)
        self.create_xp_directory()

    #def student_simulation(self, student, seq_manager_name):
    #    WorkingSession = WorkingSession(student,self.define_seq_manager(seq_manager_name))
    #    WorkingSession.run(self._nb_step)
    #    #print WorkingSession.get_WorkingSession_logs()
    #    self._groups[seq_manager_name].append(WorkingSession)

    #def population_simulation(self):
    #    for seq_manager_name in self._seq_manager_list_name:
    #        print seq_manager_name
    #        population = copy.deepcopy(self._population)
    #        for student in population:
    #            self.student_simulation(student,seq_manager_name)
    
    def create_xp_directory(self):
        datafile.create_directories([self._directory])
        final_dir = "%s/%s/" % (self._directory,self._ref_simu)
        datafile.create_directories([final_dir])

    def save(self):
        datafile.save_file(self,self._ref_simu,final_dir)

    def load(self,filename = "sim"):
        #TODO
        return

    def run(self, nb_ex = None):
        nb_ex = nb_ex or self._nb_step
        for name,group in self._groups.items():
            print name
            self.lauch_group_simulation(group, nb_ex)

    def lauch_group_simulation(self, group, nb_ex = None):
        nb_ex = nb_ex or self._nb_step
        for sub_group in group:
            sub_group.run(nb_ex)

    # Define sequence manager
    ##############################################################

    # def define_seq_manager(self,seq_manager_name, data_file_name = 'data.json'):
    #     dirf = os.path.dirname(os.path.realpath(__file__)) + "/"
    #     data_file = dirf + data_file_name
        
    #     with open(data_file, 'rb') as fp:
    #         ssb_data = json.load(fp)
        
    #     ssb_data["path"] = dirf

    #     #seq_manager_params_creation = [self.RT_main, ssb_data['levelupdate'], ssb_data['filter1'], ssb_data['filter2'], ssb_data['uniformval']]
        
    #     if seq_manager_name == "RiARiT":
    #         #seq_manager = RiaritHssbg(self.RT_main, params = ssb_data)
    #         seq_manager = RiaritHssbg(params = ssb_data[seq_manager_name])
    #     elif seq_manager_name == "ZPDES":
    #         #seq_manager = ZpdesHssbg(self.RT_main, params = ssb_data[seq_manager_name])
    #         seq_manager = ZpdesHssbg(params = ssb_data[seq_manager_name])
    #     elif seq_manager_name == "Sequence":
    #         #seq_manager = Sequence(self.RT_main, params = ssb_data[seq_manager_name])
    #         seq_manager = Sequence(params = ssb_data[seq_manager_name])
    #     else :
    #         #seq_manager = RandomSequence(self.RT_main, params = ssb_data[seq_manager_name])
    #         seq_manager = RandomSequence(params = ssb_data["Random"])
        
    #     return seq_manager

    ##############################################################
    ## Population generation functions
    ##############################################################

   
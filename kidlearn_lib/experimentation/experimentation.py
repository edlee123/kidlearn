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
        self.population = population or config.population(params = params["population"])
        self.logs = {}

        if WorkingSessions:
            self._working_sessions = WorkingSessions
        else:
            self._working_sessions = []
            for student_params in self.population:
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

    def get_ex_repartition_time(self,first_ex = 1, nb_ex=101, type_ex=["M","R","MM","RM"], 
                                nb_ex_type=[6,4,4,4]):
        
        repart = [[],[],[],[]]
        for num_ex in range(first_ex,nb_ex):
            exs = self.get_data_time(num_ex,"exercise","_act")
            for nbType in range(len(type_ex)):
                repart[nbType].append([0 for i in range(nb_ex_type[nbType])])
                #print repart
            for j in range(len(exs)):
                repart[exs[j]["MAIN"][0]][num_ex-first_ex][exs[j][type_ex[exs[j]["MAIN"][0]]][0]] += 1

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
        self._nb_students = self.params["population"]["nb_students"]
        self._nb_step = self.params["nb_step"]
        self._model_student = self.params["population"]["model"]
        
        self.do_simu_path(self.params["ref_expe"])

        
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

    def do_simu_path(self,ref = ""):
        directory = ""
        for seqName in self._seq_manager_list_name:
            directory += "%s_" % seqName[0:min(len(seqName),2)]
        directory = "%sms%s" % (directory,self._model_student)
        self._directory = directory 
        self._ref_simu = "%s_ns%s_ne%s_%s" % (directory,self._nb_students,self._nb_step,ref)

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
    
    def save(self):
        datafile.create_directories([self._directory])
        final_dir = "%s/%s/" % (self._directory,self._ref_simu)
        datafile.create_directories([final_dir])
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

    """ TO DO and rework next methods """

    # Generate population
    ##############################################################

    def define_population(self, config = None):
        self.population_generation_parameters()
        if self._model_student == "Qstudent":
            population = self.generate_qstudent_population()

        elif self._model_student == 1:
            population = self.generate_pstudent_population()

        elif self._model_student == 2:
            population = self.generate_ktstudent_population()

        elif self._model_student == 3:
            population = self.generate_ktfeatures_population()

        else:
            print "NOT GOOD STUD MODEL TYPE"

        return population

    def generate_qstudent_population(self):
        population_q_profiles = self.generate_q_profiles()
        population = []

        for stud_skills in population_q_profiles:
            params = self.params["population"]
            params["knowledge_levels"] = stud_skills
            params["knowledge_names"] = self._knowledge_names

            population.append(params)

        return population

    def generate_pstudent_population(self):
        population_p_profiles = self.generate_p_profiles()
        population_q_profiles = self.generate_q_profiles()
        population = []
        for i in range(self._nb_students):
            population.append(Pstudent(params = population_p_profiles[i],knowledge_levels = population_q_profiles[i], knowledge_names = self._knowledge_names))
        return population

    def generate_ktstudent_population(self,kt_profil = 0):
        population = []
        for i in range(self._nb_students):
            population.append(KTStudent(knowledge_names = self._knowledge_names, knowledge_params = self._KTStudent_profils[kt_profil]))
        return population

    def generate_ktfeatures_population(self,kt_profil = 0):
        population = []
        for i in range(self._nb_students):
            population.append(KTStudent(self.config.knowledges_conf))
        return population

        return population

    # Generate population parameters
    ##############################################################
    def generate_kt_parametrisation(self):

        return

    def generate_q_profiles(self):
        population_q_profiles = self.generate_normal_population(self._nb_students,self.population_skill_lvl_mean,self.population_skill_lvl_var)
        for stud in population_q_profiles:
            stud = self.correct_skill_vector(stud)
        return population_q_profiles

    def generate_normal_population(self,size_population, mean,var):
        cov = np.diag(var)
        population_normal = np.random.multivariate_normal(mean,cov,(size_population))
        #for i in range(0,len(lvl)) :
        #    print "%s max : %s min : %s" %(i, max(lvl[i]),min(lvl[i]))
        return population_normal

    def generate_p_profiles(self):
        self._nb_class = len(self._p_student_profiles)
        nbStudClass = self._nb_students/self._nb_class
        population_p_profiles = []
        for p in self._p_student_profiles:
            for i in range(0,nbStudClass):
                population_p_profiles.append(p)
        
        return population_p_profiles

    def correct_skill_vector(self,skill_vector):
        for i in [2,5]:
            if skill_vector[i] > skill_vector[i-1]:
                skill_vector[i] = skill_vector[i-1]
        for i in range(len(skill_vector)):
            if skill_vector[i] < 1 or skill_vector[i] > 1:
                skill_vector[i] = min(max(skill_vector[i],0),1)
            if i > 3: 
                if skill_vector[i] > skill_vector[i-3]:
                    skill_vector[i] = skill_vector[i-1]
            skill_vector[i] = round(skill_vector[i],2)
        return skill_vector

    def population_generation_parameters(self,skill_lvl_mean = 0, skill_lvl_var = 0):
        self._knowledge_names = ["KnowMoney","IntSum","IntSub","IntDec","DecSum","DecSub","DecDec"]
        #self.RT_main = "MAIN"
        #self._knowledge_names = ["S1","S2","S3"]
        #self.RT_main = "MAIN" #"KTTEST"


        #####################################################################################
        ##Definition of population parameters, first the skill level average
        #####################################################################################

        population_skill_lvl_mean_tab = [] #[0.7,0.8,0.5,0.1,0.1,0.1,0.1]
        population_skill_lvl_mean_tab.append([0.2,0.2,0.1,0.1,0.1,0.1,0.1])
        #population_skill_lvl_mean_tab.append([1,1,1,1,1,1,1])
        #population_skill_lvl_mean_tab.append([0.2,0.2,0.2,0.2,0,0,0])
        #population_skill_lvl_mean_tab.append([0.5,0.5,0.5,0.5,0.5,0.5,0.5])
        #population_skill_lvl_mean_tab.append([0.3,0.3,0.3,0.3,0.3,0.3,0.3])
        #population_skill_lvl_mean_tab.append([0.5,0.5,0.5,0.5,0.5,0.5,0.5])
        #population_skill_lvl_mean_tab.append([0.7,0.7,0.7,0.7,0.5,0.5,0.5])
        #population_skill_lvl_mean_tab.append([0.05,0.01,0.001,0.001,0.001,0.01,0.01])
        #population_skill_lvl_mean_tab.append([0.4,0.3,0.2,0.1,0.1,0.3,0.3])
        #population_skill_lvl_mean_tab.append([0.6,0.5,0.1,0.1,0.1,0.5,0.3])
        #population_skill_lvl_mean_tab.append([0.8,0.7,0.1,0.1,0.1,0.6])
        population_skill_lvl_mean_tab.append([1,1,0,0,0,0,0])
        
        self.population_skill_lvl_mean = population_skill_lvl_mean_tab[skill_lvl_mean]
        
        ##Second, the skill level variance
        
        population_skill_lvl_var_tab = []#[0.03,0.01,0.001,0.01,0.01,0.01,0.01]
        population_skill_lvl_var_tab.append([0,0,0,0,0,0,0])
        #population_skill_lvl_var_tab.append([0.03,0.03,0.03,0.03,0.03,0.03,0.03])
        #population_skill_lvl_var_tab.append([0.3,0.3,0.3,0.3,0.3,0.3,0.3])
        population_skill_lvl_var_tab.append([0.005,0.005,0.01,0.01,0.01,0.005,0.01])

        self.population_skill_lvl_var = population_skill_lvl_var_tab[skill_lvl_var]
        
        ################################################################################
        ## Here, we define p_student understanding profiles
        ################################################################################
        
        self._p_student_profiles = []
        self._p_student_profiles.append({"MAIN": [1],"M": [1], "R": [1],"MM": [1], "RM": [1],"mod": [1],"Car": [0],"M4": [1], "UR": [1], "DR": [1]})
        self._p_student_profiles.append({"MAIN": [2],"M": [2], "R": [2],"MM": [2], "RM": [2],"mod": [2],"Car": [1],"M4": [2], "UR": [2], "DR": [2]})
        self._p_student_profiles.append({"MAIN": [3],"M": [3], "R": [3],"MM": [3], "RM": [3],"mod": [3],"Car": [1],"M4": [3], "UR": [3], "DR": [3]})
        self._p_student_profiles.append({"MAIN": [4],"M": [4], "R": [4],"MM": [4], "RM": [4],"mod": [4],"Car": [1],"M4": [4], "UR": [4], "DR": [4]})
        #self._p_student_profiles.append({"MAIN": [0],"M": [0], "R": [0],"MM": [0], "RM": [0],"mod": [0],"Mmod": [0],"M4mod": [0]})
        #self._p_student_profiles.append({"MAIN": [3],"M": [3], "R": [3],"MM": [3], "RM": [3],"mod": [3],"Mmod": [3],"M4mod": [3]})
        #self._p_student_profiles.append({"M":[12],"mod":[2,2,0], "R": [6]}) # comprend l'écrit (e+o)

        ################################################################################
        ## Definition of KT student profils
        ################################################################################
        
        self._KTStudent_profils = []
        self._KTStudent_profils.append([{"L0" : 0.01,"T": 0.02, "G" : 0.1, "S" : 0.1}])
        #self._KTStudent_profils.append({"KnowMoney":0,"IntSum":0, "IntSub":0, "IntDec":0, "DecSum":0, "DecSub":0, "DecDec":0})

        ################################################################################
        ## Definition of KT student profils
        ################################################################################
        
        self._KTStudent_profils = []
        self._KTStudent_profils.append([{"beta_0": 0.1,"beta":[0,0,0]}])


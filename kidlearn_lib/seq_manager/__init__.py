from .hssbg import * #HierarchySSBG 
from .riarit import *  #RIARIT_hssbg
from .zpdes import * #ZPDES_hssbg
from .teacher_sequence import Sequence
from .random_sequence import Random_sequence

seq_dict_gen = {}
seq_dict_gen["RIARIT_hssbg"] = RIARIT_hssbg
seq_dict_gen["RIARIT_ssbg"] = RIARIT_ssbg
seq_dict_gen["ZPDES_hssbg"] = ZPDES_hssbg
seq_dict_gen["ZPDES_ssbg"] = ZPDES_ssbg
seq_dict_gen["Sequence"] = Sequence
seq_dict_gen["Random_sequence"] = Random_sequence
from .hssbg import * #HierarchicalSSBG 
from .riarit import *  #RiaritHssbg
from .zpdes import * #ZpdesHssbg
from .teacher_sequence import Sequence
from .random_sequence import RandomSequence

seq_dict_gen = {}
seq_dict_gen["RiaritHssbg"] = RiaritHssbg
seq_dict_gen["RiaritSsbg"] = RiaritSsbg
seq_dict_gen["ZpdesHssbg"] = ZpdesHssbg
seq_dict_gen["ZpdesSsbg"] = ZpdesSsbg
seq_dict_gen["Sequence"] = Sequence
seq_dict_gen["RandomSequence"] = RandomSequence
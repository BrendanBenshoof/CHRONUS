#this file is for various, uncatigorized or yet to be catigorized files

from hash_util import *
import node as node
import random

def estimate_nodes():
    
    pass
    
    
def make_pop(num):
	out = []
	for i in range(0,num):
		out.append(node.Node_Info("",0,generate_random_key()))
	return out

print make_pop(10)


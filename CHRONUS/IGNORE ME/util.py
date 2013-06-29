#this file is for various, uncatigorized or yet to be catigorized files

from hash_util import *
import node as node
import random
import matplotlib.pyplot as plt
import numpy, math

def estimate_nodes():
    
    pass
    
    
def make_pop(num):
    out = []
    for i in range(0,num):
        out.append(node.Node_Info("",0,generate_random_key()))
    out = sorted(out, key=lambda x: int(x.key.key,16))
    return out

def get_fingers(pop):
    ideal_fingers = map(lambda x: generate_key_with_index(x), range(0,160))
    fingers = {}
    loc = 0
    current = ideal_fingers[0]
    for i in pop:
        while hash_greater_than(i.key, current):
            fingers[loc] = i
            loc+=1
            current = ideal_fingers[loc]
    return fingers

def model(x):
    myfingers = get_fingers(make_pop(x))
    keys = set(myfingers.values())
    inv_map = {v:k for k, v in myfingers.items()}
    weighted = map(lambda x: inv_map[x],keys)
    return sum(weighted)/sum(myfingers.keys())

window = map(lambda x: 0.0, range(0,20))


def estimate(x):
    global window
    i = model(x)
    window.remove(window[0])
    window.append(i)
    #i = sum(window)/len(window) + random.random()-0.5
    return 2**i

data_x = []
data_y = []
last = 1
for i in range(1,2000)[::10]:
    sol = estimate(i)
    if i%1000 == 1:
        print i, sol
    data_x.append(i)
    data_y.append(sol)


print numpy.polyfit(data_x, data_y, 1.0)
plt.plot(data_x, data_y)
plt.show()


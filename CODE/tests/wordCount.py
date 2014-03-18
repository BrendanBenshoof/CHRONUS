jobid =  "word count"
from map_reduce import Data_Atom
import cfs

def map_func(atom):
    freqs = {}
    text = atom.contents  #temporary for testing 
    # we'll have to pull the contents of the file for the given key
    
    text = text.split()
    for word in text:
        word = word.lower()
        word = word.strip("!?.,;:\"\'*[]()/<>-*~%")
        if word is "":
            continue
        if word in freqs:
            freqs[word] = freqs[word] + 1
        else:
            freqs[word] = 1
    # print freqs
    atom = Data_Atom("", atom.hashkeyID, freqs)
    atom.jobid = jobid
    return atom
    
    
def reduce_func(atom1,atom2):
    if atom1.jobid == atom2.jobid:
        jobid = atom2.jobid
    else:
        raise Exception("unmatched jobs in reduce")
    "the form of this is probably wrong"
    a = atom1.contents
    b = atom2.contents
    for word in b:
        if word in a:
            a[word] = a[word] + b[word]
        else:
            a[word] = b[word]
    atom = Data_Atom("", atom1.hashkeyID, a)
    atom.jobid = atom1.jobid
    return atom        
    

def stage_func(filename):
    pass
    # generate the id for the keyfile from the filename
    # 
   
   
"""
# http://stackoverflow.com/questions/18761016/break-a-text-file-into-smaller-chunks-in-python
def chunk(fname):
    with open(fname, 'rb') as fin:
        return list(iter(lambda: fin.read(4096), ''))          

print chunk("constitution.txt")
"""
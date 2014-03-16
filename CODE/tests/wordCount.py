jobid =  "word count"
from map_reduce import Data_Atom


def map_func(atom):
    pass
    freqs = {}
    
    text = atom.contents  #temporary for testing 
    # we'll have to pull the contents of the file for the given key
    
    text = text.split()
    for word in text:
        word = word.lower()
        word = word.strip("!?.\"\';")
        if word in freqs:
            freqs[word] = freqs[word] + 1
        else:
            freqs[word] = 1
    print freqs
    atom = Data_Atom("", atom.hashkeyID, freqs)
    atom = jobid
    return atom
    
def reduce_func(atom1,atom2):
    if atom1.jobid == atom2.jobid:
        jobid = atom2.jobid
    else:
        raise Exception("unmatched jobs in reduce")
    "the form of this is probably wrong"
    aFreqs = atom1.contents
    bFreqs = atom2.contents
    for word in bFreqs:
        if 

def stage_func():
   pass
   
   
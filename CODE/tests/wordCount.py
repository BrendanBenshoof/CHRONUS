jobid =  "word count"
from services.cfs import Data_Atom, getCFSsingleton, KeyFile, makeKeyFile
import time
import hash_util

def map_func(atom):
    # get the atom off the disk
    #print "LOOK AT ME!!!!!!!!", type(atom.hashkeyID)
    atom = getCFSsingleton().getChunk(atom.hashkeyID)
    freqs = {}
    text = atom.contents  #temporary for testing 
    # we'll have to pull the contents of the file for the given key
    
    text = text.split()
    
    for word in text:
        word = word.lower()
        word = word.strip(" !?.,;:\"\'*[]()/<>-*~%")
        if word is u"":
            continue
        if word in freqs:
            freqs[word] = freqs[word] + 1
        else:
            freqs[word] = 1
    # print freqs
    atom = Data_Atom(freqs,atom.hashkeyID)
    return atom
    
    
def reduce_func(atom1,atom2):
    a = atom1.contents
    b = atom2.contents
    for word in b:
        if word in a:
            a[word] = a[word] + b[word]
        else:
            a[word] = b[word]
    atom = Data_Atom(a, atom1.hashkeyID)
    return atom        
    
# assumption, filename is stored on network
def stage():
    filename = ".\\tests\\constitution.txt" 
    key = makeKeyFile(filename)
    cfs = getCFSsingleton()
    cfs.writeFile(key)
    
    time.sleep(2)
    
    # generate the id for the keyfile from the filename
    hashid =hash_util.hash_str(filename)
    keyfile_raw = cfs.getChunk(hashid).contents
    keyfile = KeyFile.parse(keyfile_raw)
    atoms = []
    for key in keyfile.chunklist:
        atoms.append(Data_Atom(key,key))
    return atoms
    
"""
# http://stackoverflow.com/questions/18761016/break-a-text-file-into-smaller-chunks-in-python
def chunk(fname):
    with open(fname, 'rb') as fin:
        return list(iter(lambda: fin.read(4096), ''))          

print chunk("constitution.txt")
"""
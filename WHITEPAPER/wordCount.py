jobid =  "word count"
from services.cfs import Data_Atom, getCFSsingleton, KeyFile, makeKeyFile
import services.cfs as cfs
import time
import hash_util


def map_func(atom):
    atom = getCFSsingleton().getChunk(atom.hashkeyID)
    freqs = {}
    text = atom.contents
    
    
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

def smartChunk(x):
    return cfs.logicalChunk(cfs.binaryChunkPack(cfs.wordChunk(x)))

# assumption, filename is stored on network
def stage():
    filename = ".\\tests\\shakespeare.txt"
    key = makeKeyFile(filename,smartChunk)
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
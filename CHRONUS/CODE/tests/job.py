from map_reduce import Data_Atom
## assume contents is a line of text
def map_func(atom):
    jobid = atom.jobid
    results = {}
    print "running a map"
    line = atom.contents
    line = line.strip()
    words  = line.split()
    for word in words: 
        try: 
            results[word] = results[word]+1
        except KeyError: 
            results[word] =  1
    atom = Data_Atom("", atom.hashkeyID, results)    
    atom.jobid = jobid
    return atom


def reduce_func(atom1, atom2):
    if atom2.jobid == atom2.jobid:
        jobid = atom2.jobid
    else:
        raise Exception("unmatched jobs in reduce")
    "the form of this is probably wrong"
    results = atom1.contents
    for word, count in atom2.contents.iteritems():
        try:
           results[word] +=  count
        except KeyError:
            results[word] = count
    atom = Data_Atom("", atom1.hashkeyID, results)
    atom.jobid = atom1.jobid
    return atom


def stage():
    data  = open("accelerando.txt") 
    atoms = []
    for line in data:
        atoms.append(Data_Atom("job",None,line))
    data.close()
    return atoms

# stuff = map(map_func, atoms)
# stuff = reduce(reduce_func, stuff).contents

# for key, value in sorted(stuff.iteritems(), key = lambda x: - x[1]):
#     print key, value

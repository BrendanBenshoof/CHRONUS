from map_reduce import Data_Atom
## assume contents is a line of text
def map_func(atom):
    results = {}
    line = atom.contents
    line = line.strip()
    words  = line.split()
    for word in words: 
        try: 
            results[word] = results[word]+1
        except KeyError: 
            results[word] =  1
    return Data_Atom(atom.jobid, 0, results)


def reduce_func(atom1, atom2):
    "the form of this is probably wrong"
    results = atom1.contents
    for word, count in atom2.contents.iteritems():
        try:
            results[word] +=  count
        except KeyError:
            results[word] = count
    return Data_Atom(atom1.jobid, 0, results)



data  = open("accelerando.txt") 
atoms = []
for line in data:
    atoms.append(Data_Atom(0,0,line))

stuff = map(map_func, atoms)
stuff = reduce(reduce_func, stuff).contents

for key, value in sorted(stuff.iteritems(), key = lambda x: - x[1]):
    print key, value
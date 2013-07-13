from map_reduce import Data_Atom
## assume contents is a line of text
def map_func(atom):
    results = {}
    print "runnign a map"
    line = atom.contents
    line = line.strip()
    words  = line.split()
    for word in words: 
        try: 
            results[word] = results[word]+1
        except KeyError: 
            results[word] =  1
    atom.contents = results
    return atom


def reduce_func(atom1, atom2):
    "the form of this is probably wrong"
    results = atom1.contents
    for word, count in atom2.contents.iteritems():
        try:
           atom1.contents[word] +=  count
        except KeyError:
            atom1.contents[word] = count
    return atom1


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
##cleans out all the pyc files, record files, and chunk files
import os, sys
import fnmatch

for root, dir, files in os.walk("."):
        print root
        txtcount = 0
        pycount = 0
        for items in fnmatch.filter(files, "*.chunk"):
                os.remove(os.path.join(root,items))
                txtcount+=1
        for items in fnmatch.filter(files, "*.pyc"):
                os.remove(os.path.join(root,items))
                pycount==1
        print str(txtcount)+" chunk files removed"
        print str(pycount)+" pyc files removed"
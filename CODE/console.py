#Instrumentation Console
#You use this to controll the cluster.

import webserver
import json
import threading


class stupidPrinter(threading.Thread):
    def __init__(self,inqueue):
        self.inqueue = inqueue
        threading.Thread.__init__(self)
    def run(self):
        while(True):
            x= self.inqueue.get(True,None)
            print x

def convert(i):#de-unicodes json
    if isinstance(i, dict):
        return {convert(key): convert(value) for key, value in i.iteritems()}
    elif isinstance(i, list):
        return [convert(element) for element in i]
    elif isinstance(i, unicode):
        return i.encode('utf-8')
    else:
        return i

def pack(stuff):
    return json.dumps(stuff,separators=(',',':'))

def unpack(string):
    return convert(json.loads(string,separators=(',',':')))


directives = {"*":"command(s) for all"}

#possible commands:
#KILL, REZ, SET{key:val,key:val...}
#START{jobname}
for i in range(0,9000):
    directives[str(i)]="commands for "+str(i)


toset = {"INTERVAL":100,"JOB":"test","stuff":"otherstuff"}

directives["321"] = "SET"+pack(toset)

webResults = webserver.getQueue()
webserver.setContents(directives)

printer = stupidPrinter(webResults)
printer.start()

webserver.start()

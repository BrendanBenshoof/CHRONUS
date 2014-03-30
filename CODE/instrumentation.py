### This file is currently in brainstorm mode
### Feel free to change things

from threading import Lock, Thread
import urllib2
import json
import time

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
    return convert(json.loads(string))




###
## Experimental Values
###

# Sizes for the pi map reduce
PI_LARGE = 100000000
PI_MED   = 10000000
PI_SMALL = 1000000


#Num Jobs
JOBS_SMALL = 250
JOBS_MED   = 500
JOBS_LARGE = 1000

# Files for word count
WC_LARGE = "shakespeare.txt"
WC_SMALL = "constitution.txt"


MASTERNODE = "http://kali:9080"
MYID = 1
PERIOD = 10


TIME_SPENT_MAPREDUCE = 0
TIMELOCK = Lock()

BYTES_IN  = 0
BYTES_OUT = 0
BYTELOCK = Lock()

def addTime(t):
    global TIMELOCK, TIME_SPENT_MAPREDUCE
    TIMELOCK.aquire()
    TIME_SPENT_MAPREDUCE+=t
    TIMELOCK.release()

def getReportTime():
    global TIMELOCK, TIME_SPENT_MAPREDUCE
    TIMELOCK.acquire()
    temp = TIME_SPENT_MAPREDUCE
    TIME_SPENT_MAPREDUCE = 0
    TIMELOCK.release()
    return temp

def addBytes(chan,t):
    global BYTELOCK, BYTES_OUT, BYTES_IN
    if chan in ("IN","OUT"):
        BYTELOCK.acquire()
        if chan == "IN":
            BYTES_IN+=t
        if chan== "OUT":
            BYTES_OUT+=t
        BYTELOCK.release()

def getReportbytes():
    global BYTELOCK, BYTES_OUT, BYTES_IN
    BYTELOCK.acquire()
    output = {"IN":BYTES_IN,"OUT":BYTES_OUT}
    BYTES_IN=0
    BYTES_OUT=0
    BYTELOCK.release()
    return output

working = True

def reporter(nodeid):
    global working
    myurl = MASTERNODE+"/"+str(nodeid)
    while working:
        time.sleep(PERIOD)
        if not working:
            break
        data = (getReportbytes(),getReportTime())
        urllib2.urlopen(myurl, pack(data)).read()


t = Thread(target = lambda: reporter(MYID))
t.start()



###
## Churn simulation
###
# Should it be chance each second an event happens
# Or chance for each node to switch state?
CHURN_RATE = 0.00025  
ACTIVE_NODES = {}
INACTIVE_NODES = {}


###
##
###
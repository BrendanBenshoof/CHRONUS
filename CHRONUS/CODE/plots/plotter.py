import matplotlib.pyplot as plt
import math
from scipy.interpolate import spline


import numpy as np



# 
f = open("data_ksolve.csv","r")

n0=[1,5,10,20,30]
n1=[1,10,20,30,40]
n2=[1,10,20,30,40]

r0 = [44.81,49.5699999332,115.7799998919,235.4800000191,361.4900000095]
r1 = [431.17,131.05,86.80,106.91,191.90]
r2 = [4382.2,1082.1,483.21,430.78,686.43]

t0=r0[0]
t1=r1[0]
t2=r2[0]

# for i in range(0,len(r0)):
#     r0[i]=t0/r0[i]

# for i in range(0,len(r1)):
#     r1[i]=t1/r1[i]

# for i in range(0,len(r2)):
#     r2[i]=t2/r2[i]


k0 = []
k1 = []
k2 = []

#for l in f:
    #line = l.rstrip("\n").split(",")
    #print line
    #if line[1] != '':
        #i = float(line[1])
        #n = float(line[0])
        #n0.append(n)
        ##k0.append((i-t0/n)/math.log(n,2))
        #r0.append(i)
    #if line[2] != '':
        #i = float(line[2].rstrip("\n"))
        #n = float(line[0])
        #n1.append(n)
        ##k1.append((i-t0/n)/math.log(n,2))
        #r1.append(i)
    #if line[3] != '':
        #print line[3]
        #i = float(line[3].rstrip("\n"))
        #n = float(line[0])
        #n2.append(n)
        ##k2.append((i-t0/n)/math.log(n,2))
        #r2.append(i)
        #print n,i

#s = sum(k0)+sum(k1)+sum(k2)

xnew = np.linspace(1.0,40.0,300)



#print s/(len(k0)+len(k1)+len(k2))
#plt.plot(n0,k0,".")
#plt.plot(n1,k1,".")
#plt.plot(n2,k2,".")
#plt.show()

churn =     [0.008,  0.004,  0.000775, 0.00025, 0.000025, 0.0]
churn_dur = [191.25, 329.20, 445.47,   431.8667,331.803,  411.57]



xnew = np.linspace(min(churn),max(churn),300)
y1 = spline(churn,churn_dur,xnew)

plt.plot(churn,churn_dur,"o",label="100,000,000 sample run")
plt.legend()
plt.ylabel('time (seconds)')
plt.xlabel('likelyhood of failure per second')
plt.title("Duration versus churn")
plt.show()



xnew = np.linspace(min(n1),max(n1),300)
y1 = spline(n1,r1,xnew)
#plt.figure(2)
#b = plt.plot(xnew,y1,"-")
plt.plot(n2,r2,"ok--",label="10^9 sample job")

plt.plot(n1,r1,"ok-",label="10^8 sample job")
xnew = np.linspace(min(n0),max(n0),300)
y0 = spline(n0,r0,xnew)
#plt.figure(3)
#c = plt.plot(xnew,y0,"-")
plt.plot(n0,r0,"ok:",label="10^7 sample job")
plt.plot([50.0],[0.0],"w")


#t0=44.8099999427795
#t1=438.22
#t2=4382.2

#k0 = []
#k1 = []
#k2 = []

##for l in f:
    ##line = l.rstrip("\n").split(",")
    ##print line
    ##if line[1] != '':
        ##i = float(line[1])
        ##n = float(line[0])
        ##n0.append(n)
        ###k0.append((i-t0/n)/math.log(n,2))
        ##r0.append(i)
    ##if line[2] != '':
        ##i = float(line[2].rstrip("\n"))
        ##n = float(line[0])
        ##n1.append(n)
        ###k1.append((i-t0/n)/math.log(n,2))
        ##r1.append(i)
    ##if line[3] != '':
        ##print line[3]
        ##i = float(line[3].rstrip("\n"))
        ##n = float(line[0])
        ##n2.append(n)
        ###k2.append((i-t0/n)/math.log(n,2))
        ##r2.append(i)
        ##print n,i

# for i in range(3,10,1):
#     t_0 = 10**i
#     x = range(n_min,n_max)
#     ymean = map(lambda x: t_0/(t_0/x + k_mean*math.log(x,2)), x)

#     plt.plot(x,ymean,label="projected 10^"+str(i)+" second job")


plt.legend()
plt.ylabel('time (seconds)')
plt.xlabel('number of workers')
plt.title("Experimental Duration")
plt.show()

##print s/(len(k0)+len(k1)+len(k2))
##plt.plot(n0,k0,".")
##plt.plot(n1,k1,".")
##plt.plot(n2,k2,".")
##plt.show()




#xnew = np.linspace(min(n2),max(n2),300)
#y2 = spline(n2,r2,xnew)
##plt.figure(1)
#a = plt.plot(xnew,y2,"-")
#plt.plot(n2,r2,"ok", label="10^10 sample job")

#print r2

#xnew = np.linspace(min(n1),max(n1),300)
#y1 = spline(n1,r1,xnew)


#plt.legend()
#plt.ylabel('time (seconds)')
#plt.xlabel('number of workers')
#plt.title("Experimental times")
##plt.figure(2)
#b = plt.plot(xnew,y1,"-")
#plt.plot(n1,r1,"+k",label="10^9 sample job")
#xnew = np.linspace(min(n0),max(n0),300)
#y0 = spline(n0,r0,xnew)
##plt.figure(3)
#c = plt.plot(xnew,y0,"-")
#plt.plot(n0,r0,"xk",label="10^8 sample job")

#k_mean = 36.489
#k_stdev = 24.25

#n_min = 1
#n_max = 1000



#for i in range(3,10,1):
    #t_0 = 10**i
    #x = range(n_min,n_max)
    #ymean = map(lambda x: t_0/(t_0/x + k_mean*math.log(x,2)), x)

    #plt.plot(x,ymean,label="projected 10^"+str(i)+" second job")


#plt.legend()
#plt.ylabel('time (seconds)')
#plt.xlabel('number of workers')
#plt.title("Experimental times")




#plt.show()

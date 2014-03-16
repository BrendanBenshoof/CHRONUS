import matplotlib.pyplot as plt
import math
from scipy.interpolate import spline


import numpy as np




f = open("data_ksolve.csv","r")

n0=[1,5,10,20,30]
n1=[1,10,20,30,40]
n2=[1,10,20,30,40]
r0 = [44.81,49.5699999332,115.7799998919,235.4800000191,361.4900000095]
r1 = [438.22,126.42,82.53,87.89,214.03]
r2 = [4382.2,1082.1,483.21,430.78,686.43]

t0=44.8099999427795
t1=438.22
t2=4382.2
s0 = []
s1 = []
s2 = []


for i in r0:
    s0.append(t0/i)

for i in r1:
    s1.append(t1/i)
    
for i in r2:
    s2.append(t2/i)
    
r0 = s0
r1 = s1
r2 = s2


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




xnew = np.linspace(min(n2),max(n2),300)
y2 = spline(n2,r2,xnew)
#plt.figure(1)
#a = plt.plot(xnew,y2,"-")
plt.plot(n2,r2,"ok", label="10^10 sample job")

print r2

xnew = np.linspace(min(n1),max(n1),300)
y1 = spline(n1,r1,xnew)
#plt.figure(2)
#b = plt.plot(xnew,y1,"-")
plt.plot(n1,r1,"+k",label="10^9 sample job")
xnew = np.linspace(min(n0),max(n0),300)
y0 = spline(n0,r0,xnew)
#plt.figure(3)
#c = plt.plot(xnew,y0,"-")
plt.plot(n0,r0,"xk",label="10^8 sample job")

k_mean = 36.489
k_stdev = 24.25

n_min = 1
n_max = 1000



for i in range(3,10,1):
    t_0 = 10**i
    x = range(n_min,n_max)
    ymean = map(lambda x: t_0/(t_0/x + k_mean*math.log(x,2)), x)

    plt.plot(x,ymean,label="projected 10^"+str(i)+" second job")

plt.legend(loc=2)
plt.ylabel('Speedup (ratio)')
plt.xlabel('number of workers')
plt.title("Experimental Speedup")




plt.show()

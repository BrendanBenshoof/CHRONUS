import matplotlib.pyplot as plt
import math

f = open("data_ksolve.csv","r")

n0=[]
n1=[]
n2=[]
r0 = []
r1 = []
r2 = []

t0=44.8099999427795
t1=438.22
t2=4382.2
k0 = []
k1 = []
k2 = []

for l in f:
	l=l.rstrip()
	line = l.split(",")
	if line[1] != '':
		i = float(line[1])
		n = float(line[0])
		n0.append(n)
		k0.append((i-t0/n)/math.log(n,2))
	if line[2] != '':
		i = float(line[2])
		n = float(line[0])
		n1.append(n)
		k1.append((i-t0/n)/math.log(n,2))
	if line[3] != '':
		i = float(line[3])
		n = float(line[0])
		n2.append(n)
		k2.append((i-t0/n)/math.log(n,2))

s = sum(k0)+sum(k1)+sum(k2)
print s/(len(k0)+len(k1)+len(k2))
plt.plot(n0,k0,".")
plt.plot(n1,k1,".")
plt.plot(n2,k2,".")
plt.show()




# plt.figure(1)
# plt.plot(n2,r2,"-")
# plt.ylabel('speedup (ratio)')
# plt.xlabel('number of workers')
# plt.title("100,000,000,000 sample speedup")

# plt.figure(2)
# plt.plot(n1,r1,"-")
# plt.ylabel('speedup (ratio)')
# plt.xlabel('number of workers')
# plt.title("10,000,000,000 sample speedup")

# plt.figure(3)
# plt.plot(n0,r0,"-")
# plt.ylabel('speedup (ratio)')
# plt.xlabel('number of workers')
# plt.title("1,000,000 sample speedup")
# plt.show()
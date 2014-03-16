import matplotlib.pyplot as plt
import math

k_mean = 36.489
k_stdev = 24.25

n_min = 1
n_max = 5000


for i in range(3,10,1):
    t_0 = 10**i
    x = range(n_min,n_max)
    ymean = map(lambda x: t_0/(t_0/x + k_mean*math.log(x,2)), x)

    plt.plot(x,ymean,label="projected 10^"+str(i)+" second job")

plt.legend(loc=0)

plt.title("Projected speedup using experimental overhead")
plt.xlabel("number of workers")
plt.ylabel("speedup")
#plt.yscale('log')
plt.show()

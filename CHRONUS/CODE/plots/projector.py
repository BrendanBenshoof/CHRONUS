import matplotlib.pyplot as plt
import math

k_mean = 36.489
k_stdev = 24.25

n_min = 1
n_max = 1000

t_0 = 60*60*5

x = range(n_min,n_max)
ymean = map(lambda x: t_0/(t_0/x + k_mean*math.log(x,2)), x)
yplus = map(lambda x: t_0/(t_0/x + (k_mean+k_stdev)*math.log(x,2)), x)
yminus = map(lambda x: t_0/(t_0/x + (k_mean-k_stdev)*math.log(x,2)), x)

a,= plt.plot(x,ymean,"b")
b,= plt.plot(x,yminus,"g")
c,= plt.plot(x,yplus,"r")

plt.legend([a,b,c],["Mean experimental k value", "1 standard deviation lower experimental k value", "1 standard deviation higher experimental k value"])

plt.title("Expected Speedup of 5hr job")
plt.xlabel("number of workers")
plt.ylabel("speedup (nX)")
plt.show()
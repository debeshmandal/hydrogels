import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

data = pd.read_csv('data.out', comment='#', skiprows=4, delim_whitespace=True, header=None)

fig, ax = plt.subplots()

for i, j in [(2, 'N'), (5, 'X')]:
    ax.plot(data[1], data[i]/sum(data[i]), label=j)

ax.legend()
ax.set_xlabel('r')
ax.set_ylabel('g(r)')

fig, ax = plt.subplots()
data = pd.read_csv('gyr.out', comment='#', header=None, delim_whitespace=True)
ax.plot(data[0], data[1])
ax.set_xlabel('time')
ax.set_ylabel('gyration')

fig, ax = plt.subplots()
ax.plot(data[0], data[2])
ax.set_xlabel('time')
ax.set_ylabel('mesh size')

plt.show()
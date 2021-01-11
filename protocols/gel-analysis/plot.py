import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

class Model:
    def __init__(self, folder):
        self._gyr = 'out.gyr'
        self._rdf = 'out.rdf'
        self._rho_N = 'out.rho.N'
        self._rho_X = 'out.rho.X'
    
    @property
    def json(self):
        return

    @property
    def rdf(self):
        return

    @property
    def gyration(self):
        return

def plot_rdf(ax):
    data = pd.read_csv(
        'out.rdf',
        delim_whitespace=True,
        header=None,
        skiprows=4,
    )
    delta = data[1][1] - data[1][0]
    ax.bar(data[1] - delta/4, data[2], width=delta/2, label='N')
    ax.bar(data[1] + delta/4, data[5], width=delta/2, label='X')
    ax.legend(frameon=False)
    ax.set_xlabel(r"$r$  $[\sigma]$")
    ax.set_ylabel(r"$g(r)$")
    return

def plot_rho(ax):
    data = pd.read_csv(
        'out.rho.N',
        delim_whitespace=True,
        header=None,
        skiprows=4,
    )
    ax.bar(data[1], data[3]/(4 * np.pi * data[1] ** 2 * (data[1][1]-data[1][0])), label='N')
    ax.set_xlabel(r"$r$  $[\sigma]$")
    ax.set_ylabel(r"$\rho(r)$")
    return

def main():
    fig, ax = plt.subplots(2)
    plot_rdf(ax[0])
    plot_rho(ax[1])
    plt.show()


if __name__ == '__main__':
    main()

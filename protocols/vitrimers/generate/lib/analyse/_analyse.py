import pandas as pd
import numpy as np
from scipy.spatial.distance import pdist

class Model:
    def __init__(
        self, 
        particles: pd.DataFrame, 
        edges: pd.DataFrame,
        *args
    ):
        self.particles = particles
        self.edges = edges

    def rdf(self, crosslinkers=False, **kwargs):
        positions = self.particles[['x', 'y', 'z']]
        if crosslinkers:
            positions = self.particles[['x', 'y', 'z', 'crosslinker']]
            positions = positions[positions['crosslinker']]
            positions = positions[['x', 'y', 'z']]

        positions = positions.to_numpy()
        distances = pdist(positions)
        histogram, bins = np.histogram(distances, **kwargs)
        histogram = histogram / sum(histogram)
        
        bins = np.array(bins[:-1])
        #histogram = histogram / (4 * np.pi * (bins ** 2))
        array = np.stack([bins, histogram])
        return array

    def neighbours(self):
        return

    def density(self):
        return

    def gyration_tensor(self):
        return

    def sphericity(self):
        return

    def gyration(self):
        return

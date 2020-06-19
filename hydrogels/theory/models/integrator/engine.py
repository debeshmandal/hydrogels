import numpy as np
import pandas as pd

class History():
    def __init__(self, sim_obj : Simulation, **kwargs):
        self._simulation = sim_obj
        self.data = {}

        self.initialise()

    def initialise(self):
        # read variables and setup data dictionary
        self.data = self._simulation.variables

    def update(self):
        for key, value in self._simulation.variables.items():
            self.data[key].append(value)
        return

    @property
    def dataframe(self) -> pd.DataFrame:
        df = pd.DataFrame(self.data)
        times = [i*self._simulation.dt for i in self._simulation.timestep]
        return

class Simulation():
    def __init__(self, dt, **kwargs):
        self.dt = dt

        self._variables = {}
        self._equations = {}
        
        self.history = History(self, **kwargs)
        pass

    def state(self):
        return

    def integrate(self):

        self._history.update()
        return

    def add_equation(self, input_variables, output_variables, function):
        return

    @property
    def variables(self):
        return self._variables

    @property
    def equations(self):
        return self._equations

    def run(self, n_timesteps):
        for timestep in n_timesteps:
            self.integrate()
        return 
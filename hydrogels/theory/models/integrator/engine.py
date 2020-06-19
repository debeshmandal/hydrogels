import numpy as np
import pandas as pd
from typing import List
import functools

class Equation():
    def __init__(self, function, parameters : List[str] = [], output_variable : str = None, string : str = ''):
        self._function = function

        # set parameters
        if parameters == []:
            self.parameters = [i for i in self._function.__annotations__.keys() if i != 'return']
        else:
            self.parameters = parameters

        # set output vairable
        if output_variable != None:
            self.output = output_variable
        else:
            self.output = self._function.__annotations__.get('return', None)
        if self.output == None:
            raise ValueError('Set output using function annotation or with output_variable kwarg!')

        # set description
        self._string = f'{function.__name__} := {string}'

    def __call__(self, input_dict):
        parameters = {}
        for key in self.parameters:
            parameters[key] = input_dict[key]
        return self._function(**parameters)

    @property
    def string(self):
        return self._string

class History():
    def __init__(self, sim_obj, **kwargs):
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
        times = [i * self.meta['constants']['dt'] for i in self._simulation.timestep]
        df['t'] = times
        return df
    
    @property
    def meta(self) -> dict:
        data = {
            'constants' : self._simulation.constants,
            'equations' : [i.string for i in self._simulation.equations]
        }
        return data

class Simulation():
    def __init__(self, dt, constants={}, variables={}, equations : List[Equation] = [], **kwargs):

        self._constants = constants
        self._constants['dt'] = dt
        self._variables = variables
        self._equations = equations

        self.history = History(self, **kwargs)

    def integrate(self):
        for equation in self.equations:
            self._variables[equation.output] = equation(self._variables)

        self._history.update()
        return

    def add_equation(self, equation : Equation):
        self._equations.append(equation)
        self.history.initialise()

    @property
    def constants(self):
        return self._constants

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


if __name__ == '__main__':
    print('Running Test...')

    dictionary = {'t' : 10}

    print('Testing functions with dict vs kwargs:')

    def test_fn_dict(input_dict):
        value = input_dict.get('t', 1)
        return f'\tUsing test_fn_dict: {value}'

    print(test_fn_dict(dictionary))

    def test_fn_kwargs(t=1):
        value = t
        return f'\tUsing test_fn_kwargs: {value}'
    
    print(test_fn_kwargs(**dictionary))

    print('Setting up Equation:')
    def func(M : float = 1.0, R : float = 1.0, dt : float = 1.0) -> 'R':
        """M x (R^-2) x dt"""
        print(f'\tfrom func: M={M}, R={R}, dt={dt}')
        if R == 0:
            return 0.0
        return R - (M * R ** -2) * dt

    equation = Equation(func, string=func.__doc__)
    result = equation({
        'M' : 1,
        'R' : 2,
        'dummy' : 3,
        'dt' : 1
    })
    print(f'\tResult from equation: {result}')
    print(f'\tString from equation: {equation.string}')

    print('Setting up simulation:')
    print('Doing a single step:')
    print('Doing multiple steps:')
    print('Recording History:')



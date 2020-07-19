import hydrogels.theory.models as models

def test_cxx():
    from hydrogels.theory.models import potentials, functions
    assert potentials.zero(1) == 0
    potentials.lennard_jones(1,1,2,1)
    potentials.macro_LJ(1,1,0.1,3,1,5)
    functions.radius_from_number(1.0, 1.0)
    assert functions.boltzmann(1.0, 0.0) == 1.0
    return

def test_utils():
    return

def test_integrator():
    import hydrogels.theory.models.integrator as integrator
    integrator.Simulation(1)
    return

def test_engine():
    from hydrogels.theory.models.integrator import Simulation, Equation, History
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
        return R - (1./(M  * R ** 2)) * dt

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
    simu = Simulation(
        0.1, 
        variables= {
            'M' : 5,
            'R' : 10
        },
        equations = [equation]
    )
    print(f'\tsimu.variables: {simu.variables}')
    print(f'\tsimu.constants: {simu.constants}')
    print(f'\tsimu.inputs: {simu.inputs}')
    print(f'\tsimu.equations: {simu.equations}')
    print(f'\tsimu.history.meta: {simu.history.meta}')
    print(f'\tsimu.history.dataframe:\n{simu.history.dataframe}')
    print('Doing a single step:')
    simu.integrate()
    print(f'\tsimu.history.dataframe:\n{simu.history.dataframe}')
    print('Doing multiple steps:')
    simu.run(100)
    print(f'\tsimu.history.dataframe:\n{simu.history.dataframe}')
    print(f'Simulation with 2 equations:')
    def func_2(R : float = 1) -> 'M':
        """M=R/2"""
        return R/2

    equation_2 = Equation(func_2, string=func_2.__doc__)

    simu = simu = Simulation(
        0.1, 
        variables= {
            'M' : 5,
            'R' : 10
        },
        equations = [equation, equation_2]
    )
    simu.run(100)
    print(f'\tsimu.history.dataframe:\n{simu.history.dataframe}')

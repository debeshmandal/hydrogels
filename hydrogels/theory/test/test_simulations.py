from hydrogels.theory.models.integrator import Equation

def test_constant_density():
    from hydrogels.theory.models.simulations import ConstantDensity
    def equation():
        def func(R: float = 0, K: float = 1.0, rc: float = 10.) -> 'V':
            """ harmonic with cutoff """
            if R == 0:
                return 0.
            elif R > rc:
                return 0.
            else:
                return K * R ** -2
            return
        return Equation(func, string=func.__doc__)
    simu = ConstantDensity(
        0.1,
        equation(),
        N = 10000,
        constants = {
            'K' : 1.0,
            'rc' : 1.0
        }
    )
    simu.integrate()
    simu.run(1000)
    return

def test_lennard_jones():
    from hydrogels.theory.models.simulations import LennardJones
    simu = LennardJones(0.1, 10, **{
                'sig' : 1.0,
                'eps' : 1.0,
                'rc' : 5.0, 
                'beta' : 1.0,
                'c0' : 5.0,
                'nV' : 1.0,
                'rate': 0.1,
                'thickness': 0.01
            })
    simu.integrate()
    simu.run(10)
    return

if __name__ == '__main__':
    test_constant_density()
    test_lennard_jones()
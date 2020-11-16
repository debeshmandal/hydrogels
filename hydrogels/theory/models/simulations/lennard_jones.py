from ..integrator import Simulation, Equation
import hydrogels.potentials as potentials
import hydrogels.functions as functions

class LennardJones(Simulation):
    def __init__(self, dt, N, **constants):
        super().__init__(
            dt, 
            constants = {
                'sig' : constants['sig'],
                'eps' : constants['eps'],
                'rc' : constants['rc'], 
                'beta' : constants['beta'],
                'c0' : constants['c0'],
                'base_rate' : constants['rate'],
                'nV' : constants['nV'],
                'thickness' : constants['thickness'],
                'rE' : constants['rE']
            },
            variables = {
                'N' : N,
                'R' : None,
                'V' : None,
                'k' : None,
                'KV' : None,
            },
            equations= self.equations
        )

    @property
    def potential(self) -> Equation:
        def func(
            sig: float = 1.,
            eps: float =1., 
            rc: float = 5.0, 
            R: float = 2.0, 
            nV: float = 0.0,
            rE: float = 0.0,
        ) -> 'V':
            """Macroscopic Lennard-Jones 12-6"""
            return potentials.macro_LJ(sig, eps, nV, 12, rE, R) - potentials.macro_LJ(sig, eps, nV, 6, rE, R)
        return Equation(func, string=func.__doc__)

    @property
    def equations(self) -> list:
        def radius(N: int = 0, nV: float = 1.0) -> 'R':
            """Radius from number of particles and density"""
            return functions.radius_from_number(N, nV)

        def rate(V: float = 0.0, beta: float = 1.0, KV: float = 1.0, c0: float = 1.0) -> 'k':
            """rate from potential, concentratin and rate of encounter"""
            return functions.rate_from_potential_energy(KV, c0, V, beta)

        def number(N: int = 0, k: float = 1.0, dt: float = 1.0) -> 'N':
            """New number from old number and rate"""
            return functions.update_number_from_rate(N, k, dt)

        def KV(R: float = 0.0, base_rate: float = 0.0, thickness: float = 0.0) -> 'KV':
            """Rate for unit volume in the shell of the reaction"""
            return functions.kv_from_radius(R, base_rate, thickness)

        return [
            Equation(radius, string=radius.__doc__),
            self.potential,
            Equation(KV, string=KV.__doc__),
            Equation(rate, string=rate.__doc__),
            Equation(number, string=number.__doc__),
        ]

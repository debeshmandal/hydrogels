from ..integrator import Simulation, Equation
import potentials

class ConstantDensity(Simulation):
    def __init__(self, dt, potential_equation, **kwargs):
        self._potential_equation = potential_equation
        super().__init__(
            dt, 
            constants = {
                'sig' : sig,
                'eps' : eps,
                'rc' : rc, 
                'beta' : kwargs.get('beta', 1.0),
                'c0' : kwargs.get('c0', 1.0),
                'KV' : kwargs.get('KV', 1.0),
                'nV' : kwargs.get('nV', 1.0)
            }
            variables = {
                'N' : N,
                'R' : None,
                'V' : None,
                'k' : None
            },
            equations= self.equations
        )

    @property
    def potential(self):
        return self._potential_equation
    
    @property
    def equations(self) -> list:
        def radius(N: int = 0, nV: float = 1.0) -> 'R':
            """Radius from number of particles and density"""
            return functions.R_from_N(N, nV)

        def rate(V: float = 0.0, beta: float = 1.0, KV: float = 1.0, c0: float = 1.0) -> 'k':
            """rate from potential, concentratin and rate of encounter"""
            return functions.rate_from_boltzmann(KV, c0, beta, V)

        def number(N: int = 0, k: float = 1.0, dt: float = 1.0) -> 'N':
            """New number from old number and rate"""
            return functions.N_update_from_rate(N, k, dt)

        return [
            Equation(radius, string=radius.__doc__),
            self.potential
            Equation(rate, string=rate.__doc__),
            Equation(number, string=number.__doc__),
        ]
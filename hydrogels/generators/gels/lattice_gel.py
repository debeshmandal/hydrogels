from .lennard_jones import LennardJonesGel

class LatticeGel(LennardJonesGel):
    def __init__(self, *args, **kwargs):
        pass

    def initialise_geometry(self, N, V, nV, R, spacing):

        # We only want one out of spacing and nV
        if spacing != None and nV != None:
            raise ValueError('Only provide one of either spacing and nV')
        elif nV:
            # set spacing here, and have nV property later
            self.spacing = nV ** -0.357
        elif spacing:
            nV = spacing ** -2.8
            self.spacing = spacing
        
        density_checker = True if (spacing or nV) else False


        # Check that only one of R and V are provided and create
        # boolean to store this information
        if R != None and V != None:
            raise ValueError('Only provide one of either R and V')
        if R:
            self.radius = R
        elif V:
            self.radius = np.cbrt(0.75 * (1./np.pi) * V)

        geometry_checker = True if (R or V) else False

        if density_checker and geometry_checker:
            # radius and spacing have been calculated
            pass
        elif N:
            if not density_checker:
                self.spacing = self._get_spacing(N)
            elif not geometry_checker:
                self.radius = self._get_radius(N)
            else:
                raise TypeError('You have not provided [R|V] or [spacing|nV]')
        else:
            raise TypeError('Since you have not provided [R|V] and [spacing|nV], you must provide N')

        if self.spacing < 0.0:
            raise ValueError(
                f'Increase the density (i.e. N) because the model only '
                f'works for high density systems and N is currently {N} which '
                f'means that the spacing is {self.spacing}!'
            )
        
        # generate positions
        self.positions = self.generate_positions()

    def _get_radius(self, N: int) -> float:
        _volume = float(N) / (self.spacing ** -2.8)
        _radius = np.cbrt(0.75 * (1./np.pi) * _volume)
        return _radius

    def _get_spacing(self, N: int) -> float:
        _nV = N / self.volume
        _spacing = _nV ** -0.357
        return _spacing

    @property
    def N(self) -> float:
        return len(self.positions)

    @property
    def nV(self) -> float:
        return self.N / self.volume

    @property
    def volume(self) -> float:
        return 4./3. * np.pi * self.radius ** 3

    def generate_positions(self) -> np.ndarray:
        """
        Generate positions within a sphere
        """
        n_gridpoints = int((self.radius * 2.) / self.spacing) + 1
        positions = pd.DataFrame(
            np.array(
                [
                    [i, j, k] for i, j, k in \
                        product(
                            range(n_gridpoints), 
                            range(n_gridpoints), 
                            range(n_gridpoints)
                        )
                ]
            ) * self.spacing - self.radius
        ).rename(columns={
            0: 'x',
            1: 'y',
            2: 'z',
        })
        print(self.spacing, self.radius, n_gridpoints)
        print(positions)
        
        positions = positions[
            np.sqrt(
                positions['x'] ** 2 \
                + positions['y'] ** 2 \
                + positions['z'] ** 2
            ) <= self.radius + self.spacing / 2
        ].reset_index(drop=True)
        return positions.values

    def generate_edges(self, positions, n=6) -> np.ndarray:
        """Create bonding topology for gel object"""
        # create dataframe of indices sorted by distance
        pairs = np.argsort(
            pd.DataFrame(
                squareform(pdist(positions))
            )
        ).iloc[:, 1 : 1+n]

        # create nested list of pairs
        result = []
        for idx in pairs.index:
            for pair in pairs.loc[idx]:
                result.append([idx, pair])

        # return as array
        return np.array(result)
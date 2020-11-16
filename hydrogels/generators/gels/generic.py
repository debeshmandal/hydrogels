from .core import Gel

class GenericGel(Gel):
    def __init__(self, fname: str, **kwargs):
        _box, _positions, _edges = self.read_oxDNA(fname)
        self._box = np.array(_box)
        self._positions = np.array(_positions)
        self._edge_list = _edges
        super().__init__(np.array(self._box), **kwargs)

    def read_oxDNA(self):
        positions = []
        with open(oxdna_bonds, 'r') as f:
            N = int(f.readline().split()[2])
            edges = []
            box = [float(i) for i in f.readline().split()[:3]]
            
            for i in range(N):
                positions.append([float(i) for i in f.readline().split()])
            print(pd.DataFrame(positions))
            for i in range(N):
                index, n_bonds = [int(i) for i in f.readline().split()]
                edges.append([int(i) for i in f.readline().split()])
                assert len(edges[index-1]) == n_bonds
            print(pd.DataFrame(edges, dtype=int))           

        return box, positions, edges

    @property
    def positions(self):
        return self._positions

    def generate_edges(self, *args, **kwargs):
        edges = []
        for i, indices in self._edge_list:
            for j in indices:
                edges.append([i, j])
        return edges
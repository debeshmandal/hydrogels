#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <cstdlib>
#include <memory>

using namespace std;

struct CSDParticle {
  int idx;
  int cluster;
  vector<int> neighs;
  
  CSDParticle(int n_idx) {
    idx = n_idx;
    cluster = n_idx;
  }
};

using Particle = unique_ptr<CSDParticle>;

void flip_neighs(vector<Particle> &particles, int i, vector<int> &clusters) {
  auto *p = particles[i].get();
  for(int n_idx: p->neighs) {
    auto *q = particles[n_idx].get();
    if(q->cluster > p->cluster) {
      clusters[q->cluster]--;
      q->cluster = p->cluster;
      clusters[p->cluster]++;

      flip_neighs(particles, n_idx, clusters);
    }
  }
}

int main(int argc, char *argv[]) {
  if(argc < 3) {
    cerr << "Usage is " << string(argv[0]) << " bond_conf topology [configuration]" << endl;
    exit(1);
  }

  ifstream in(argv[2]);
  int N, NA;
  in >> N >> NA;
  int NB = N - NA;
  in.close();

  bool print_conf = (argc > 3);

  vector<int> clusters(N, 1);
  vector<int> csd(N + 1, 0);
  vector<Particle> particles(N);

  in.open(argv[1]);
  char buff_line[1024];
  in.getline(buff_line, 1024);
  in.getline(buff_line, 1024);
  for(int i = 0; i < N; i++) in.getline(buff_line, 1024);
  for(int i = 0; i < N; i++) {
    int idx, n_neighs;
    in >> idx >> n_neighs;
    idx--;

    particles[i] = Particle(new CSDParticle(idx));    
    for(int nn = 0; nn < n_neighs; nn++) {
      int neigh;
      in >> neigh;
      neigh--;
      particles[i]->neighs.push_back(neigh);
    }
  }
  in.close();

  for(int i = 0; i < N; i++) flip_neighs(particles, i, clusters);

  int largest = 0;
  for(int i = 0; i < N; i++) {
    if(clusters[i] > clusters[largest]) largest = i;
    csd[clusters[i]] += 1;
  }

  cout << "Clusters:" << endl;
  for(int c = 0; c < N; c++) {
    int size = clusters[c];
    if(size > 0) cout << c << " " << size << endl;
  }

  cout << endl << "CSD:" << endl;
  for(int c = 1; c <= N; c++) {
    int size = csd[c];
    if(size > 0) cout << c << " " << size << endl;
  }

  if(print_conf) {
    in.open(argv[3]);

    ofstream out(string("largest_bonds.dat"));

    char line[1024];
    in.getline(line, 1024);
    out << line << endl;
    in.getline(line, 1024);
    out << line << endl;
    in.getline(line, 1024);
    out << line << endl;

    int new_NA = 0;
    int new_NB = 0;
    for(auto &p: particles) {
      in.getline(line, 1024);
      if(p->cluster == largest) {
	out << line << endl;
	if(p->idx < NA) new_NA++;
	else new_NB++;
      }
    }
    
    out.close();
    in.close();

    int new_N = new_NA + new_NB;
    out.open(string("largest_topology.dat"));
    out << new_N << " " << new_NA << endl;
    out.close();
  }

  return 0;
}

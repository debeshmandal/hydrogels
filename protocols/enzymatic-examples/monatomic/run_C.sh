ID=C
for i in {1..4}; do
  python monatomic.py $ID$i.yml -n $ID$i --run
done
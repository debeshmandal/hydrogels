ID=C
for i in {1..4}; do
  python cube.py yml/$ID$i.yml -n $ID$i --run  -s 3
done
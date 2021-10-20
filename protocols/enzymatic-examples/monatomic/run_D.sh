ID=D
for i in {1..4}; do
  python monatomic.py yml/$ID$i.yml -n $ID$i --run
done
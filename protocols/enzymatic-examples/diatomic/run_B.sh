ID=B
for i in {1..5}; do
  python diatomic.py yml/$ID$i.yml -n $ID$i --run -s 3
done
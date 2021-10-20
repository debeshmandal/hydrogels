ID=A
for i in {1..5}; do
  python monatomic.py yml/$ID$i.yml -n $ID$i --run
done

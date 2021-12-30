bash package.sh
mkdir run
pushd run
cp ../package.tar.gz .
tar xzf package.tar.gz
python main.py settings.yml
popd run
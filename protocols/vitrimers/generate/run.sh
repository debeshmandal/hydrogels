bash package.sh
mkdir -p run
pushd run
cp ../package.tar.gz .
tar xzf package.tar.gz
python main.py settings.yml
popd
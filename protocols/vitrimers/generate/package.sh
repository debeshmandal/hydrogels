rm -rf package.tar.gz
cp settings.yml lib
pushd lib
tar czf package.tar.gz ./*
mv package.tar.gz ..
popd
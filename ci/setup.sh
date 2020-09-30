if [[ "$TRAVIS_OS_NAME" != "linux" ]]; then
  echo "LINUX"
elif [[ "$TRAVIS_OS_NAME" == "osx" ]]; then
  echo "OSX"
elif [[ "$TRAVIS_OS_NAME" == "windows" ]]; then
  echo "WINDOWS"
fi;
FILE="mypl-v1.0.0.deb"
if [ -f $FILE ]; then
  echo linting
  lintian $FILE
else
        echo building then linting
        make build
        dpkg -i $FILE
        lintian $FILE
fi

#! /bin/sh
cd tests
# [-p pattern] is optional
if [ "$1" = 'nose' ]; then
    nosetests -v
elif [ "$1" = '-v' ]; then
    python -m unittest discover . -p 'test_*.py'
else
    python -m unittest discover . -p 'test_*.py' 1>/dev/null
fi

#!/bin/sh
echo "Checking if code meets PEP8 by Flake8."
python -m flake8
echo "Checking if code meets lint rules by pylint."
find . -type d -d 1 -not -path './.*' -not -path './mock_cas' -not -path './scripts/' -not -path './htmlcov' | xargs python -m pylint
echo "Running unit tests and coverage test."
python -m coverage run manage.py test --debug-mode
python -m coverage report --skip-covered

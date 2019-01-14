#!/bin/sh
echo "Checking if code meets PEP8 by Flake8."
python -m flake8
echo "Checking if code meets lint rules by pylint."
find . -maxdepth 1 -type d -not -path './.*' -not -path './mock_cas' -not -path './scripts' -not -path './htmlcov' -not -path '.' | xargs python -m pylint
echo "Running unit tests and coverage test."
python -m coverage run manage.py test --debug-mode
python -m coverage report --skip-covered

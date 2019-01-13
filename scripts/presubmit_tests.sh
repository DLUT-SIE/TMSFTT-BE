echo "Checking if code meets PEP8 by Flake8."
flake8
echo "Checking if code meets lint rules by pylint."
pylint auth infra training_program training_record training_review TMSFTT
echo "Running unit tests and coverage test."
coverage run manage.py test --debug-mode
coverage report --skip-covered

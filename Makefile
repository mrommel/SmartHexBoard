# define the name of the virtual environment directory
VENV := venv

# default target, when make executed without arguments
all: venv

$(VENV)/bin/activate: requirements.txt
	python3.12 -m venv $(VENV)
	./$(VENV)/bin/pip3.12 install --upgrade setuptools
	# ./$(VENV)/bin/pip3.12 install --upgrade distribute
	./$(VENV)/bin/pip3.12 install -r requirements.txt
	#./$(VENV)/bin/pip3.12 install --force-reinstall -r requirements.txt --only-binary=:all:

# venv is a shortcut target
venv: $(VENV)/bin/activate

pylint: venv
	# --disable=C0303,R0903,R0915,C0103,E1101,E0102,R0913,W0123,R0912,R0801 simulation map population
	./$(VENV)/bin/pylint smarthexboard

# tests: venv
#	./$(VENV)/bin/python3.12 -m unittest

tests: venv
	./$(VENV)/bin/pytest -q smarthexboard/tests.py
	./$(VENV)/bin/pytest -q smarthexboard/test_service.py

run-qcluster: venv
	./$(VENV)/bin/python3.12 manage.py qcluster

run: venv
	rm -rf django_smarthexboard_cache
	./$(VENV)/bin/python3.12 -m pip install --upgrade pip
	./$(VENV)/bin/python3.12 manage.py runserver 8081

clean:
	rm -rf $(VENV)
	find . -type f -name '*.pyc' -delete

makemigrations: venv
	./$(VENV)/bin/python3.12 manage.py makemigrations
	./$(VENV)/bin/python3.12 manage.py sqlmigrate smarthexboard 0010
	./$(VENV)/bin/python3.12 manage.py migrate

migrate: venv
	./$(VENV)/bin/python3.12 manage.py migrate

preparetranslations: venv
	./$(VENV)/bin/python3.12 manage.py makemessages -l de -l en -e html,txt,py --ignore=venv/*

compiletranslations: venv
	./$(VENV)/bin/python3.12 manage.py compilemessages --ignore=venv/*

createsuperuser: venv
	./$(VENV)/bin/python3.12 manage.py createsuperuser


# make sure that all targets are used/evaluated even if a file with same name exists
.PHONY: all venv run clean tests
# define the name of the virtual environment directory
VENV := venv

# default target, when make executed without arguments
all: venv

$(VENV)/bin/activate: requirements.txt
	python3 -m venv $(VENV)
	./$(VENV)/bin/pip install -r requirements.txt

# venv is a shortcut target
venv: $(VENV)/bin/activate

pylint: venv
	# --disable=C0303,R0903,R0915,C0103,E1101,E0102,R0913,W0123,R0912,R0801 simulation map population
	./$(VENV)/bin/pylint smarthexboard

# tests: venv
#	./$(VENV)/bin/python3 -m unittest

tests: venv
	./$(VENV)/bin/pytest -q smarthexboard/tests.py

run-qcluster: venv
	./$(VENV)/bin/python3 manage.py qcluster

run: venv
	./$(VENV)/bin/python3 manage.py runserver 8081

clean:
	rm -rf $(VENV)
	find . -type f -name '*.pyc' -delete

migrate: venv
	./$(VENV)/bin/python3 manage.py migrate


createsuperuser: venv
	./$(VENV)/bin/python3 manage.py createsuperuser


# make sure that all targets are used/evaluated even if a file with same name exists
.PHONY: all venv run clean tests
ifeq (, $(ENV))
	env := development
else ifeq (test, $(ENV))
	env := testing
else
	env := $(ENV)
endif

app := pyramid_secure_response

setup:
	pip install -e '.[${env}]' -c constraints.txt
.PHONY: setup

check:
	flake8
.PHONY: check

lint:
	pylint test ${app}
.PHONY: lint

vet: | check lint
.PHONY: vet

test:
	ENV=test py.test -c setup.cfg -s -q
.PHONY: test

coverage:
	ENV=test py.test -c setup.cfg -s -q --cov=${app} --cov-report \
	  term-missing:skip-covered
.PHONY: coverage

clean:
	find . ! -readable -prune -o \
	  ! -path "*./.git/*" ! -path "./venv/*" \
	  ! -path "./doc/*" -print | \
	  grep -E "(__pycache__|\.egg-info|\.pyc|\.pyo)" | \
	  xargs echo
.PHONY: clean

build:
	python setup.py sdist
.PHONY: build

.DEFAULT_GOAL = coverage
default: coverage

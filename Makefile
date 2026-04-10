RM		= rm -rf

FLAKE		= flake8 .

MYSOFT		= mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

MYSTRICT	= mypy . --strict

PIP		= pip install

install:
	$(PIP) -r requirements.txt

venv:
	python3 -m venv .venv

run:
	python3 a_maze_ing.py config.txt

debug:
	python3 -m pdb a_maze_ing.py

lint:
	$(FLAKE) & $(MYSOFT)

lint-strict:
	$(FLAKE) & $(MYSTRICT)

clean:
	$(RM) __pycache__ mazegen/__pycache__ mazegen/*/__pycache__ *.env .mypy_cache

package:
	$(PIP) build && python3 -m build && $(PIP) dist/mazegen-*.whl	

.phony: install venv run debug lint lint-strict clean package

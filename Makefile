PYTEST_OPTIONS := --tb=line -rN

black := black
autoflake := autoflake --in-place --recursive --remove-unused-variables --expand-star-imports --remove-all-unused-imports

all: fmt typecheck check

fmt:
	$(autoflake) .
	isort .
	$(black) .

typecheck:
	mypy --strict .

check:
	python -m  pytest $(PYTEST_OPTIONS)

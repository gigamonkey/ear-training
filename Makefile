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


graph.dot: make_graph.py
	./make_graph.py > $@

graph.pdf: graph.dot
	dot -T pdf graph.dot -o graph.pdf

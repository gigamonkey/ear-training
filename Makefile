autoflake_options := --remove-unused-variables --expand-star-imports --remove-all-unused-imports

fmt:
	autoflake --in-place --recursive $(autoflake_options) .
	isort .
	black .

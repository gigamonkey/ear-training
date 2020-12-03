fmt:
	autoflake --in-place --remove-unused-variables --expand-star-imports --remove-all-unused-imports --recursive .
	isort .
	black .

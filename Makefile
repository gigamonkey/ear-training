fmt:
	isort .
	autoflake --in-place --remove-unused-variables --recursive .
	black .

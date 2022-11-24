all: test

test:
	tox

clean:
	@find . -name '*.pyc' -delete
	@rm -rf tmp \
	   src/ua_parser.egg-info \
	   dist \
	   build \
	   src/ua_parser/_regexes.py
format:
	@black .

release: clean
	pyproject-build
	twine upload -s dist/*

.PHONY: all test clean format release

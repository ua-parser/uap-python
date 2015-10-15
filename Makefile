PWD = $(shell pwd)

all: prep test 

prep:
	#git submodule update --init
	#sudo apt-get install python-yaml
	
test:
	@#test ! -d tmp && mkdir tmp
	@export PYTHONPATH=tmp && python setup.py develop -d tmp
	@# run all tests
	@python ua_parser/user_agent_parser_test.py
	@# run a single test
	@#python ua_parser/user_agent_parser_test.py ParseTest.testStringsDeviceBrandModel

clean:
	@rm -f ua_parser/user_agent_parser.pyc\
	   ua_parser/regexes.yaml\
	   ua_parser/regexes.json
	@rm -rf tmp\
	   ua_parser.egg-info\
	   dist\
	   build

.PHONY: all clean

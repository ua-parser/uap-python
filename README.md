#uap-python
A python implementation of the UA Parser (https://github.com/ua-parser, formerly https://github.com/tobie/ua-parser)

##Installing

In the top-level directory run:
```
make Makefile
```

##Getting Started

### retrieve data on a user-agent string
```
>>> import user_agent_parser
>>> import pprint
>>> pp = pprint.PrettyPrinter(indent=4)
>>> ua_string = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.104 Safari/537.36'
>>> parsed_string = user_agent_parser.Parse(ua_string)
>>> pp.pprint(parsed_string)
{   'device': {   'brand': None, 'family': 'Other', 'model': None},
    'os': {   'family': 'Mac OS X',
              'major': '10',
              'minor': '9',
              'patch': '4',
              'patch_minor': None},
    'string': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.104 Safari/537.36',
    'user_agent': {   'family': 'Chrome',
                      'major': '41',
                      'minor': '0',
                      'patch': '2272'}}
```


### extract browser data from user-agent string

```
>>> import user_agent_parser
>>> import pprint
>>> pp = pprint.PrettyPrinter(indent=4)
>>> ua_string = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.104 Safari/537.36'
>>> parsed_string = user_agent_parser.ParseUserAgent(ua_string)
>>> pp.pprint(parsed_string)
 {   'family': 'Chrome', 
	 'major': '41', 
	 'minor': '0', 
	 'patch': '2272'}
```

### extract OS information from user-agent string

```
>>> import user_agent_parser
>>> import pprint
>>> pp = pprint.PrettyPrinter(indent=4)
>>> ua_string = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.104 Safari/537.36'
>>> parsed_string = user_agent_parser.ParseOS(ua_string)
>>> pp.pprint(parsed_string)
{   'family': 'Mac OS X',
    'major': '10',
    'minor': '9',
    'patch': '4',
    'patch_minor': None}
```

### extract Device information from user-agent string


```
>>> import user_agent_parser
>>> import pprint
>>> pp = pprint.PrettyPrinter(indent=4)
>>> ua_string = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.104 Safari/537.36'
>>> parsed_string = user_agent_parser.ParseDevice(ua_string)
>>> pp.pprint(parsed_string)
{   'brand': None, 
	'family': 'Other', 
	'model': None}
```


## Copyright

Copyright 2008 Google Inc. See ua_parser/LICENSE for more information 


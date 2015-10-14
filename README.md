<<<<<<< HEAD
#uap-python
A python implementation of the UA Parser (https://github.com/ua-parser, formerly https://github.com/tobie/ua-parser)

##Build Status

[![Build Status](https://travis-ci.org/ua-parser/uap-python.svg)](https://travis-ci.org/ua-parser/uap-python)

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

=======
uap-core [![Build Status](https://secure.travis-ci.org/ua-parser/uap-core.png?branch=master)](https://travis-ci.org/ua-parser/uap-core)
========

This repository contains the core of [BrowserScope][2]'s original [user agent string parser][3]: data collected over the years by [Steve Souders][4] and numerous other contributors, extracted into a separate [YAML file][5] so as to be reusable _as is_ by implementations in any programming language.

This repo itself does _not_ contain a parser: only the necessary data to build one. There exists a ref implementation, along with multiple, production-ready implementations in various programming languages.

Maintainers
-----------

* [Lindsey Simon](https://github.com/elsigh) ([@elsigh](https://twitter.com/elsigh))
* [Tobie Langel](https://github.com/tobie) ([@tobie](https://twitter.com/tobie))

Communication channels
-----------------------

* \#ua-parser on freenode <irc://chat.freenode.net#ua-parser>
* [mailing list](https://groups.google.com/forum/#!forum/ua-parser)

Contributing Changes to regexes.yaml
------------------------------------

Please read the [contributors' guide](CONTRIBUTING.md)

License
-------

The data contained in `regexes.yaml` is Copyright 2009 Google Inc. and available under the [Apache License, Version 2.0][6].

[2]: http://www.browserscope.org
[3]: http://code.google.com/p/ua-parser/
[4]: http://stevesouders.com/
[5]: https://raw.github.com/ua-parser/uap-core/master/regexes.yaml
[6]: http://www.apache.org/licenses/LICENSE-2.0
>>>>>>> 0adc0716a0976ea0472a43d32e7c7a5f584b4e30

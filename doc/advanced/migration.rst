===============
From 0.x to 1.0
===============

Don't Touch A Thing
===================

The first and simplest way to transition is to not transition: the 0.x
API won't be removed for a long time, possibly ever. While it is
unlikely to get updated any further and will eventually (hopefully?)
fall behind, if you can't be arsed you probably don't have to until an
unlikely 2.0.

Unavoidable Divergences
=======================

Although the 1.0 API aims to be reasonably bridge-able to
0.x-compatible code, a few items may be cause for concern and require
special attention:

- The 1.0 API supports :data:`ua_parser.UserAgent.patch_minor
  <ua_parser.UserAgent>`, which may be a concern if the program stores
  match results and compares them exactly.
- The global parser of the 1.0 API is instantiated lazily on-demand,
  this may cause unexpected runtime loads and can be remediated by
  explicitly accessing the parser on load e.g.::

      import ua_parser
      # force initialisation of global parser
      ua_parser.parser

- The 1.0 API defaults to an :class:`re2-based parser
  <ua_parser.re2.Resolver>` if |re2|_ is installed, although it seems
  unlikely you may wish to consider replacing it with configuring a
  :class:`~ua_parser.Parser` with a :class:`ua_parser.basic.Resolver`
  if |re2|_ is one of your dependencies.

Default Ruleset
===============

While the 1.0 API was designed to better respect :pep:`8` and support
:mod:`typing`, it was also designed to easily be transitioned from.

Given a 0.x API not using YAML, the conversion should be very easy and
consists of:

- updating the import from ``ua_parser.user_agent_parser`` to just
  ``ua_parser``
- lowercasing the function names
- adding :meth:`~ua_parser.Result.with_defaults()` after the function
  call
- wrapping the entire thing in :func:`dataclasses.asdict`

For example, given

..
    >>> from pprint import pprint
    >>> ua_string = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.104 Safari/537.36'

.. code-block:: pycon

  >>> from ua_parser import user_agent_parser
  >>> pprint(user_agent_parser.Parse(ua_string))  # doctest: +NORMALIZE_WHITESPACE
  {'device': {'brand': 'Apple', 'family': 'Mac', 'model': 'Mac'},
   'os': {'family': 'Mac OS X',
          'major': '10',
          'minor': '9',
          'patch': '4',
          'patch_minor': None},
   'string': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 '
             '(KHTML, like Gecko) Chrome/41.0.2272.104 Safari/537.36',
   'user_agent': {'family': 'Chrome',
                  'major': '41',
                  'minor': '0',
                  'patch': '2272'}}

the 1.0 version would be:

.. code-block:: pycon

  >>> import dataclasses
  >>> import ua_parser
  >>> pprint(dataclasses.asdict(ua_parser.parse(ua_string).with_defaults()))  # doctest: +NORMALIZE_WHITESPACE
  {'device': {'brand': 'Apple', 'family': 'Mac', 'model': 'Mac'},
   'os': {'family': 'Mac OS X',
          'major': '10',
          'minor': '9',
          'patch': '4',
          'patch_minor': None},
   'string': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 '
             '(KHTML, like Gecko) Chrome/41.0.2272.104 Safari/537.36',
   'user_agent': {'family': 'Chrome',
                  'major': '41',
                  'minor': '0',
                  'patch': '2272',
                  'patch_minor': '104'}}

.. note::

   - by default, the 1.0 API simply leaves entries ``None`` when no
     data was matched, :meth:`~ua_parser.Result.with_defaults()`
     fills them with the default value for the domain matching the 0.x API
   - the 1.0 API returns :class:`typed dataclasses rather than untyped
     dicts <ua_parser.core.UserAgent>`, hence the necessary conversion
     to dict

YAML Ruleset
============

The 1.0 API does not support :envvar:`UA_PARSER_YAML` anymore, instead
it provides a layered API which lets clients use multiple parsers at
the same time, and load rulesets from various datasources.

Legacy YAML support can be added via a pretty small shim::

  import ua_parser
  from ua_parser.loaders import load_yaml

  if yaml_path = os.environ.get("UA_PARSER_YAML"):
      ua_parser.parser = ua_parser.Parser.from_matchers(
          load_yaml(yaml_path))

This will load the YAML file, create a parser from it, and set the new
parser as the global parser used by the top-level utility functions.

.. seealso::

   - :ref:`guide-custom-rulesets`
   - :ref:`guide-custom-global-parser`
   - :ref:`api-loading`


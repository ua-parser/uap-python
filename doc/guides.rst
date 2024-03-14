======
Guides
======

Custom Rulesets
===============

ua-parser defaults to the version of `ua-core
<https://github.com/ua-parser/uap-core/blob/master/regexes.yaml>`_
current when it was packaged, using a precompiled version of
``regexes.yaml``.

That is a suitable defaut, but there are plenty of reasons to use
custom rulesets:

- trim down the default ruleset to only the most current or relevant
  rules for efficiency e.g. you might not care about CalDav or podcast
  applications
- add new rules relevant to your own traffic but which don't (possibly
  can't) be in the main project
- experiment with the creation of new rules
- use a completely bespoke ruleset to track UA-identified API clients

ua-parser provides easy ways to load custom rolesets:

- :mod:`ua_parser.loaders` converts whatever external storage format
  the rules are in to internal
- :meth:`ua_parser.Parser.from_matchers` can directly create a parser
  from the loaded data, using the default resolver stack

.. code-block:: python

   from ua_parser import Parser
   from ua_parser.loaders import load_yaml # requires PyYaml

   parser = Parser.from_matchers(load_yaml("regexes.yaml"))
   parser.parse(some_ua)

Custom Global Parser
====================

The global utility functions :func:`~ua_parser.parse`,
:func:`~ua_parser.parse_user_agent`, :func:`~ua_parser.parse_os`, and
:func:`~ua_parser.parse_device` just call to the global
:data:`ua_parser.parser` internally.

This means it's possible to customise their behaviour by just
*setting* the global parser, although obviously that affects all users
in the process which is both the advantage and risk

.. code-block:: pycon

   >>> import ua_parser
   >>> import ua_parser.loaders

   >>> ua_parser.parse("foo")
   Result(user_agent=None, os=None, device=None, string='foo')
   >>> ua_parser.parser = ua_parser.Parser.from_matchers(
   ...    ua_parser.loaders.load_data((
   ...        [{"regex": "(foo)"}],
   ...        [],
   ...        [],
   ...    ))
   ... )
   >>> ua_parser.parse("foo") # doctest: +NORMALIZE_WHITESPACE
   Result(user_agent=UserAgent(family='foo',
                               major=None,
                               minor=None,
                               patch=None,
                               patch_minor=None),
          os=None,
          device=None,
          string='foo')

Cache Customisation
===================

.. todo::

   - how to build a custom resolver stack and wrap it in a parser
   - minor discussion of caches
   - maybe link to an advanced document about the specifics of
     individual caches and their memory consumption?

Writing Custom Resolvers
========================

.. todo::

   - explanation of the resolver protocol
   - maybe a fanout resolver as demo?

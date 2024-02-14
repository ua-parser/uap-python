uap-python
==========

Official python implementation of the `User Agent String
Parser <https://github.com/ua-parser>`_ project.

Build Status
------------

.. image:: https://github.com/ua-parser/uap-python/actions/workflows/ci.yml/badge.svg
   :alt: CI on the master branch

⚠️ THIS IS NOT THE DOCUMENTATION YOU ARE LOOKING FOR (probably) ⚠️
------------------------------------------------------------------

This is the readme for the `future 1.0 <https://github.com/ua-
parser/uap-python/milestone/1>`_.

For the current releases, see `the 0.x branch
<https://github.com/ua-parser/uap-python/tree/0.x#uap- python>`_.

Installing
----------

Just add ``ua-parser`` to your project's dependencies, or run

.. code-block:: sh

    $ pip install ua-parser

to install in the current environment.

Getting Started
---------------

Retrieve all data on a user-agent string
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    >>> from ua_parser import parse
    >>> ua_string = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.104 Safari/537.36'
    >>> parse(ua_string) # doctest: +NORMALIZE_WHITESPACE, +ELLIPSIS
    ParseResult(user_agent=UserAgent(family='Chrome',
                                     major='41',
                                     minor='0',
                                     patch='2272',
                                     patch_minor='104'),
                os=OS(family='Mac OS X',
                      major='10',
                      minor='9',
                      patch='4',
                      patch_minor=None),
                device=Device(family='Mac',
                              brand='Apple',
                              model='Mac'),
                string='Mozilla/5.0 (Macintosh; Intel Mac OS...

Any datum not found in the user agent string is set to ``None``::

    >>> parse("")
    ParseResult(user_agent=None, os=None, device=None, string='')

Extract only browser data from user-agent string
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    >>> from ua_parser import parse_user_agent
    >>> ua_string = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.104 Safari/537.36'
    >>> parse_user_agent(ua_string)
    UserAgent(family='Chrome', major='41', minor='0', patch='2272', patch_minor='104')

For specific domains, a match failure just returns ``None``::

    >>> parse_user_agent("")

Extract OS information from user-agent string
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    >>> from ua_parser import parse_os
    >>> ua_string = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.104 Safari/537.36'
    >>> parse_os(ua_string)
    OS(family='Mac OS X', major='10', minor='9', patch='4', patch_minor=None)

Extract device information from user-agent string
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    >>> from ua_parser import parse_device
    >>> ua_string = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.104 Safari/537.36'
    >>> parse_device(ua_string)
    Device(family='Mac', brand='Apple', model='Mac')

Parser
~~~~~~

Parsers expose the same functions (``parse``, ``parse_user_agent``,
``parse_os``, and ``parse_device``) as the top-level of the package,
however these are all *utility* methods.

The actual protocol of parsers, and the one method which must be
implemented / overridden is::

    def __call__(self, str, Components, /) -> ParseResult:

It's similar to but more flexible than ``parse``:

- The ``str`` is the user agent string.
- The ``Components`` is a hint, through which the caller requests the
  domain (component) they are looking for, any combination of
  ``Components.USER_AGENT``, ``Components.OS``, and
  ``Components.DEVICE``. ``Domains.ALL`` exists as a convenience alias
  for the combination of all three.

  The parser *must* return at least the requested information, but if
  that's more convenient or no more expensive it *can* return more.
- The ``ParseResult`` is similar to ``CompleteParseResult``, except
  all the attributes are ``Optional`` and it has a ``components:
  Components`` attribute which specifies whether a component was never
  requested (its value for the user agent string is unknown) or it has
  been requested but could not be resolved (no match was found for the
  user agent).

  ``ParseResult.complete()`` convert to a ``CompleteParseResult`` if
  all the components are set, and raise an exception otherwise. If
  some of the components are set to ``None``, they'll be swapped for a
  default value.

Calling the parser directly is part of the public API. One of the
advantage is that it does not return default values, as such it allows
more easily differentiating between a non-match (= ``None``) and a
default fallback (``family = "Other"``).

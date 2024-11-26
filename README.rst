uap-python
==========

Official python implementation of the `User Agent String
Parser <https://github.com/ua-parser>`_ project.

Build Status
------------

.. image:: https://github.com/ua-parser/uap-python/actions/workflows/ci.yml/badge.svg
   :target: https://github.com/ua-parser/uap-python/actions/workflows/ci.yml?query=branch%3Amaster
   :alt: CI on the master branch

.. image:: https://readthedocs.org/projects/uap-python/badge/?version=latest
   :target: https://uap-python.readthedocs.io/en/latest/
   :alt: Documentation Status

Installing
----------

Add ``ua-parser[regex]`` to your project's dependencies, or run

.. code-block:: sh

    $ pip install 'ua-parser[regex]'

to install in the current environment.

ua-parser supports CPython 3.9 and newer, recent pypy (supporting
3.10), and GraalPy 24.

.. note::

   The ``[regex]`` feature is *strongly* recommended:

   - ``[re2]`` is slightly slower and only works with cpython, though
     it is still a great option then (and is more memory-efficient).
   - Pure python (no feature) is *significantly* slower, especially on
     non-cpython runtimes, but it is the most memory efficient even
     with caches.

   See `builtin resolvers`_ for more explanation of the tradeoffs
   between the different options.

.. _builtin resolvers: https://uap-python.readthedocs.io/en/latest/guides.html#builtin-resolvers

Quick Start
-----------

Retrieve all data on a user-agent string
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    >>> from ua_parser import parse
    >>> ua_string = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.104 Safari/537.36'
    >>> parse(ua_string) # doctest: +NORMALIZE_WHITESPACE, +ELLIPSIS
    Result(user_agent=UserAgent(family='Chrome',
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
    Result(user_agent=None, os=None, device=None, string='')

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

Upgrading
---------

Upgrading from 0.x? See `the upgrade guide`_.

.. _the upgrade guide: https://uap-python.readthedocs.io/en/latest/advanced/migration.html

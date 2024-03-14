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

Installing `google-re2 <https://pypi.org/project/google-re2/>`_ is
*strongly* recommended as it leads to *significantly* better
performances. This can be done directly via the ``re2`` optional
dependency:

.. code-block:: sh

    $ pip install 'ua_parser[re2]'

If ``re2`` is available, ``ua-parser`` will simply use it by default
instead of the pure-python resolver.

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

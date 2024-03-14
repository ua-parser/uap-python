============
Installation
============

Python Version
==============

ua-parser currently supports Python 3.8 and newer, as well as recent
versions of PyPy supporting the same standards.

.. note:: While PyPy is supported, it is not *fast*, and google-re2 is
          not supported on it.

Installation
============

.. include:: ../README.rst
   :start-line: 23
   :end-before: Quick Start

Optional Dependencies
=====================

ua-parser currently has two optional dependencies, |re2|_ and
|pyyaml|_. These dependencies will be detected and used automatically
if installed, but can also be installed via and alongside ua-parser:

.. code-block:: sh

   $ pip install 'ua-parser[re2]'
   $ pip install 'ua-parser[yaml]'
   $ pip install 'ua-parser[re2,yaml]'


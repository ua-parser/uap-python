============
Installation
============

Python Version
==============

ua-parser currently supports CPython 3.9 and newer, recent Pypy
(supporting 3.10), and Graal 24.

.. note::

   While pypy and graal are supported, they are rather slow when using
   pure python mode and ``[re2]`` is not supported, so using the
   ``[regex]`` feature is very strongly recommended.

Installation
============

.. include:: ../README.rst
   :start-line: 23
   :end-before: Quick Start

Optional Dependencies
=====================

ua-parser currently has three optional dependencies, |regex|_, |re2|_ and
|pyyaml|_. These dependencies will be detected and used augitomatically
if installed, but can also be installed via and alongside ua-parser:

.. code-block:: sh

   $ pip install 'ua-parser[regex]'
   $ pip install 'ua-parser[re2]'
   $ pip install 'ua-parser[yaml]'
   $ pip install 'ua-parser[regex,yaml]'


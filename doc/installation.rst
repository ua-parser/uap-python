============
Installation
============

Installation
============

.. include:: ../README.rst
   :start-line: 14
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

``yaml`` enables the ability to :func:`load rulesets from yaml
<ua_parser.loaders.load_yaml>`.

The other two features enable more efficient resolvers. By default,
``ua-parser`` will select the fastest resolver it finds out of the
available set (regex > re2 > python).

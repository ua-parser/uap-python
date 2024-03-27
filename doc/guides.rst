======
Guides
======

.. _guide-custom-rulesets:

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

.. _guide-custom-global-parser:

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

Cache And Other Advanced Parser Customisation
=============================================

While loading custom rulesets has built-in support, other forms of
parser customisations don't and require manually instantiating and
composing :class:`~ua_parser.Resolver` objects.

The most basic such customisation is simply configuring caching away
from the default setup.

As an example, in the default configuration if |re2|_ is available the
RE2-based resolver is not cached, a user might consider the memory
investment worth it and want to reconfigure the stack for a cached
base.

The process is uncomplicated as the APIs are designed to compose
together.

The first step is to instantiate a base resolver, instantiated with
the relevant :class:`Matchers` data::

    import ua_parser.loaders
    import ua_parser.re2
    base = ua_parser.re2.Resolver(
        ua_parser.loaders.load_lazy_builtins())

The next step is to instantiate the cache [#cache]_ suitably
configured::

    cache = ua_parser.Cache(1000)

And compose the base resolver and cache together::

    resolver = ua_parser.caching.CachingResolver(
        base,
        cache
    )

Finally, for convenience a :class:`ua_parser.Parser` can be wrapped
around the resolver, and that can either be used as-is, or set as the
global parser for all the library users to use this new configuration
from here on::

    ua_parser.parser = ua_parser.Parser(resolver)

.. note::

   To be honest aside from configuring the presence, algorithm, and
   size of caches there currently isn't much to compose that's built
   in. The only remaining member of the cast is
   :class:`~ua_parser.caching.Local`, which is also caching-related,
   and serves to use thread-local caches rather than a shared cache.

Writing Custom Resolvers
========================

It is unclear if there would be any fun or profit to it, but an
express goal of the new API is to allow writing and composing
resolvers, so what is a resolver?

:class:`~ua_parser.Resolver` is a structural :py:class:`typing.Protocol` for
implementation convenience (nothing to inherit, and not even a class
to write). Here it is in full::

    class Resolver(Protocol):
        @abc.abstractmethod
        def __call__(self, ua: str, domain: Domain, /) -> PartialResult:
            ...

So a :class:`~ua_parser.Resolver` is just a callable which takes a
string and a :class:`~ua_parser.Domain`, and returns a
:class:`~ua_parser.PartialResult`.

For our first resolver, let's say that we have an API and a mobile
application, and as we expect the mobile application to be the main
caller we want to special-case it, we could do it in many ways but the
way we're doing it is a bespoke :class:`~ua_parser.Resolver` which
matches the application's user agent and performs trivial parsing::

    def foo_resolver(ua: str, domain: Domain, /) -> PartialResult:
        if not ua.startswith('fooapp/'):
            # not our application, match failure
            return PartialResult(domain, None, None, None, ua)

        # we've defined our UA as $appname/$version/$user-token
        app, version, user = ua.split('/', 3)
        major, minor = version.split('.')
        return PartialResult(
            domain,
            UserAgent(app, major, minor),
            None,
            Device(user),
            ua,
        )

This resolver is not hugely interesting as it resolves a very limited
number of user agent strings and fails everything else, although it
does demonstrate two important requirements of the protocol:

- If a domain is requested, it must be returned, even if ``None``
  (signaling a matching failure).
- If it's efficient there is nothing wrong with returning data for
  domains which were not requested, at worst they will be ignored.

For a more interesting resolver, we can write a *fallback* resolver:
it's a higher-order resolver which tries to call multiple
sub-resolvers in sequence until the UA is resolved. This means we
could then use something like::

    Parser(FallbackResolver([
        foo_resolver,
        re2.Resolver(load_lazy_builtins()),
    ]))

to prioritise cheap resolving of our application while still resolving
third party user agents::

  class FallbackResolver:
      def __init__(self, resolvers: List[Resolver]) -> None:
          self.resolvers = resolvers

      def __call__(self, ua: str, domain: Domain, /) -> PartialResult:
          if domain:
              for resolver in self.resolvers:
                  r = resolver(ua, domain)
                  # if any value is non-none the resolver found a match
                  if r.user_agent_string is not None \
                    or r.os is not None \
                    or r.device is not None:
                      return r

          # if no resolver found a match (or nothing was requested),
          # resolve to failure
          return PartialResult(domain, None, None, None, ua)

.. [#cache] If it has been written yet, see :doc:`advanced/caches` for
  way too much information you probably don't care about if you just
  want to parse user agent stings.

  The tldr is that bigger increases hit rates which decreases costs
  but uses more memory, and while really easy to write in Python an
  :class:`~ua_parser.caching.Lru` is a pretty bad cache all things
  considered.

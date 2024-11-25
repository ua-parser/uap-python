=========
On Caches
=========

Evaluating Caches
=================

UA-Parser tries to provide a somewhat decent cache by default, but
cache algorithms react differently to traffic patterns, and setups can
have different amounts of space to dedicate to cache overhead.

Thus, ua-parser also provides some tooling to try and evaluate
fitness, in the form of two built-in command-line scripts. Both
scripts take a mandatory *sample file* in order to provide evaluation
on representative traffic. Thus this sample file should be a
representative sample of your real world traffic (no sorting, no
deduplicating, ...).

``python -mua_parser hitrates``
-------------------------------

As its name indicates, the ``hitrates`` script allows measuring the
hit rates of ua-parser's available caches by simulating cache use at
various sizes on the sample file. It also provides the memory overhead
of each cache implementation at those sizes, both in total and per
entry.

.. warning::

   The cache overhead does not include the size of the cached entries
   themselves, which is generally 500~700 bytes for a complete entry
   (all three domains matched).

``hitrates`` also includes Bélády's MIN (aka OPT) algorithm for
reference. MIN is not a practical cache as it requires knowledge of
the future, but it provides the theoretical upper bound at a given
cache size (very theoretical, practical cache algorithms tend to be
way behind until cache sizes close in on the total number of unique
values in the dataset).

``hitrates`` has the advantage of being very cheap as it only
exercises the caches themselves and barely looks at the data.

``python -mua_parser bench``
----------------------------

``bench`` is much more expensive in both CPU and wallclock as it
actually runs the resolvers on the sample file, combined with various
caches of various sizes. For usability, it can report its data (the
average parse time per input entry) in both human-readable text with
one result per line and CSV with resolver configurations as the
columns and cache sizes as the rows.

``hitrates`` is generally sufficient as generally speaking for the
same base resolver performances tend to more or less follow hit rates:
a cache hit is close to free compared to a cache miss. Although this
is truer for the basic resolver (for which misses tend to be very
expensive). ``bench`` is mostly useful to validate or tie-break
decisions based on ``hitrates``, and allows creating nice graphs in
your spreadsheet software of choice.

Cache Algorithms
================

[S3-FIFO]_
----------

[S3-FIFO]_ is a novel fifo-based cache algorithm. It might seem odd to
pick that as default rather than a "tried and true" LRU_, but the
principles are interesting and on our sample it shows very good
performances for an acceptable implementation complexity.

Advantages
''''''''''

- excellent hit rates
- thread-safe on hits
- excellent handling of one hit wonders (entries unique to the data
  set) and rare fews (multiple entries with a lot of separation)
- flexible implementation

Drawbacks
'''''''''

- O(n) eviction
- somewhat demanding on memory, especially at small sizes

Space
'''''

An S3Fifo of size n is composed of:

- one :ref:`dict` of size 1.9*n
- three :ref:`deque` of sizes 0.1 * n, 0.9 * n, and 0.9 * n

[SIEVE]_
--------

[SIEVE]_ is an other novel fifo-based algorithm, a cousin of S3Fifo it
works off of somewhat different principle. It has good performances
and a more straightforward implementation than S3, but it is strongly
wedded to linked lists as it needs to remove entries from the middle
of the fifo (whereas S3 uses strict fifo).

Advantages
''''''''''

- good hit rates
- thread-safe on hits
- memory efficient

Drawbacks
'''''''''

- O(n) eviction

Space
'''''

A SIEVE of size n is composed of:

- a :ref:`dict` of size n
- a linked list with n :ref:`nodes of 4 pointers each <class>`

LRU
---

The grandpappy of non-trivial cache eviction, it's mostly included as
a safety in case users encounter workloads for which the fifo-based
algorithms completely fall over (do report them, I'm sure the authors
would be interested).

Advantages
''''''''''

- basically built in the Python stdlib (via
  :class:`~collections.OrderedDict`)
- O(1) eviction
- nobody ever got evicted for using an LRU

Drawbacks
'''''''''

- must be synchronised on hit: entries are moved
- poor hit rates

Space
'''''

An LRU of size n is composed of:

- an :ref:`ordered dict <odict>` of size n

Memory analysis of Python objects
=================================

Measures as of Python 3.11, on a 64b platform. Information is the
overhead of the object itself, not the data it stores e.g. if an
object stores strings the sizes of the strings are not included in the
calculations.

.. _class:

``class``
---------

With ``__slots__``, a Python object is 32 bytes + 8 bytes for each
member. An additional 8 bytes is necessary for weakref support
(slotted objects in UA-Parser don't have weakref support).

Without ``__slots__``, a Python object is 48 bytes plus an instance
:ref:`dict`.

.. note:: The instance dict is normally key-sharing, which is not
          included in the analysis, see :pep:`412`.

.. _dict:

``dict``
--------

Python's ``dict`` is a relatively standard hash map, but it has a bit
of a twist in that it stores the *entries* in a dense array, which
only needs to be sized up to the dict's load factor, while the shallow
array used for hash lookups (which needs to be sized to match
capacity) only holds indexes into the dense array. This also allows
the *size* of the indices to only be as large as needed to index into
the dense array, so for small dicts the sparse array is an array of
bytes (8 bits).

*However* because the dense array of entries is used as a stack (only
the last entry can be replaced) in case a dict "churns" (entries get
added and removed without the size changing) if the size of the dict
is close to the next break-point it would need to be compacted
frequently leading to poor performances.

As a result, although a dictionary being created or added to will be
just the next size up a dict with a lot of churn will be two sizes up
to limit the amout of compaction necessary e.g. 10000 entries would
fit in ``2**14`` (capacity 16384, for a usable size of 10922) but the
dict may be sized up to ``2**15`` (capacity 32768, for a usable size
of 21845).

Python dicts also have a concept of *key kinds* which influences parts
of the layout. As of 3.12 there are 3 kinds called
``DICT_KEYS_GENERAL``, ``DICT_KEYS_UNICODE``, and ``DICT_KEYS_SPLIT``.
This is relevant here because UA-Parser caches are keyed on strings,
which means they should always use the ``DICT_KEYS_UNICODE`` kind.

In the ``DICT_KEYS_GENERAL`` layout, each entry of the dense array has
to store three pointer-sized items: a pointer to the key, a pointer to
the value, and a cached version of the key hash. However since strings
memoize their hash internally, the ``DICT_KEYS_UNICODE`` layout
retrieves the hash value from the key itself when needed and can save
8 bytes per entry.

Thus the space necessary for a dict is:

- the standard 4 pointers object header (``prev``, ``next``, and type
  pointers, and reference count)
- ``ma_size``, 8 bytes, the number of entries
- ``ma_version_tag``, 8 bytes, deprecated
- ``ma_keys``, a pointer to the dict entries
- ``ma_values``, a pointer to the split values in ``DICT_KEYS_SPLIT``
  layout (not relevant for UA-Parser)

The dict entries then are:

- ``dk_refcnt``, an 8 bytes refcount (used for the ``DICT_KEYS_SPLIT``
  layout)
- ``dk_log2_size``, 1 byte, the total capacity of the hash map, as a
  power of two
- ``dk_log2_index_bytes``, 1 byte, the size of the sparse indexes
  array in bytes, as a power of two, it essentially memoizes the log2
  size of the sparse indexes array by incrementing ``dk_log2_size`` by
  3 if above 32, 2 if above 16, and 1 if above 8

  .. note::

     This means the dict bumps up the indexes array a bit early to
     avoids having to resize again within a ``dk_log2_size`` e.g. at
     171 elements the dict will move to size 9 (total capacity 512,
     usable capacity 341) and the index size will immediately get
     bumped to 10 even though it can still fit ~80 additional items
     with a u8 index.

- ``dk_kind``, 1 byte, the key kind explained above
- ``dk_version``, 4 bytes, used for some internal optimisations of
  cpython
- ``dk_usable``, 8 bytes, the number of usable entries in the dense array
- ``dk_nentries``, 8 bytes, the number of used entries in the dense
  array, this can't be computed from ``dk_usable`` and
  ``dk_log2_size`` because ??? from the mention of ``DKIX_DUMMY`` I
  assume it's because ``dk_usable`` is used to know when the dict
  needs to be compacted or resized, and because python uses open
  addressing and leaves tombstone (``DKIX_DUMMY``) in the sparse array
  they matter for collision performances, and thus load calculations
- ``dk_indices``, the sparse array of size
  ``1<<dk_log2_size_index_bytes``
- ``dk_entries``, the dense array of size
  ``USABLE_FRACTION(1<<dk_log2_size) * 16``

  .. note:: ``USABLE_FRACTION`` is 2/3

Thus the space formula for dicts -- in the context of string-indexed
caches -- is::

    32 + 32 + 32
      + 2**(ceil(log2(n)) + 1) * ceil(log256(n))
      + floor(2/3 * 2**ceil(log2(n)) + 1) * 16

.. _odict:

``collections.OrderedDict``
---------------------------

While CPython has a pure-python ``OrderedDict`` it's not actually
used, instead a native implementation with a native doubly linked list
and a bespoke secondary hashmap is used, leading to a much denser
collection than achievable in Python. The broad strokes are similar
though:

- a regular ``dict`` links keys to values
- a secondary hashmap links keys to *nodes* of the linked list,
  allowing reordering entries easily

The secondary hashmap is only composed of a dense array of nodes,
using the internal details of the dict in order to handle lookups in
the sparse array and collision resolution. Unlike ``dict`` however
it's sized to the dict's capacity rather than ``USABLE_FRACTION``
thereof.

The entire layout is:

- a full dict object (see above), inline
- pointers to the first and last nodes of the doubly linked list
- a pointer to the array of nodes
- ``od_fast_nodes_size``, 8 bytes, which is used to see if the
  underlying dict has been resized
- ``*od_resize_sentinel`` which is *also* used to see if the
  underlying dict has been redized (a pointer to the dict entries
  object)
- ``od_state``, 8 bytes, to check for concurrent mutations during
  iteration
- ``od_inst_dict``, 8 bytes, used to provide a fake ``__dict__`` and
  better imitate
- ``od_inst_dict``, 8 bytes, weakref support

And each node in the linked list is 4 pointers: previous, next, key,
and hash.

.. note::

   Hash is (likely) to speed up lookup since going from odict node to
   dict entry requires a full lookup, and such a lookup is what
   happens during iteration, except it uses a regular
   ``PyDict_GetItem`` instead of a low-level lookup, why?

So the ordereddict space requirement formula is::

  dict(n) + 64 + 8 * 2**(ceil(log2(n)) + 1) + 32 * n

Because it matches dict's, like dict's the capacity is double what's
strictly required due to amortising churn.

.. _deque:

``collections.deque``
---------------------

Deque is an unrolled doubly linked list of order 64, that is every
node of the linked list stores 64 items, plus two pointers for the
previous and next links. Note that the deque always allocates a block
upfront (nb: why not allocate on use?).

The deque metadata (excluding the blocks) is 232 bytes:

- the 32 bytes standard object of an object header (next pointer,
  previous pointer, refcount, and type pointer)
- the ``ob_size`` of a VAR_OBJ, apparently used to store the number of
  items as the deque does not track its blocks size
- pointers to the left and right blocks
- offsets into the left and right blocks (as they may only be
  partially filled)
- ``state``, a mutation counter used to track mutations during
  iteration
- ``maxlen``, in case the deque is length-bounded
- ``numfreeblocks``, the actual size of the freelist
- ``freelist``, 16 pointers to already allocated available blocks
- ``weakreflist``, the weakref support pointer

So the deque space requirement formula is::

  232 + max(1, ceil(n / 64)) * 66 * 8

:func:`~functools.lru_cache`
----------------------------

While not strictly relevant to ua-parser, it should be noted that
:func:`~functools.lru_cache` is *not* built on
:class:`~collections.OrderedDict`, it has its own native
implementation which uses a single dict and a different bespoke doubly
linked list with larger nodes (9 pointers).

.. [S3-FIFO] Juncheng Yang, Yazhuo Zhang, Ziyue Qiu, Yao Yue, Rashmi
    Vinayak. 2023. FIFO queues are all you need for cache eviction.
    SOSP '23. https://dl.acm.org/doi/10.1145/3600006.3613147

.. [SIEVE] Yazhuo Zhang, Juncheng Yang, Yao Yue, Ymir Vigfusson,
    K. V. Rashmi. 2023. SIEVE is Simpler than LRU: an Efficient
    Turn-Key Eviction Algorithm for Web Caches. NSDI24.
    https://junchengyang.com/publication/nsdi24-SIEVE.pdf

from __future__ import annotations

import abc
import dataclasses
import threading
from collections import OrderedDict, deque
from contextvars import ContextVar
from typing import (
    Callable,
    Deque,
    Dict,
    Optional,
    Protocol,
    Union,
)

from .core import Domain, PartialParseResult, Resolver

__all__ = [
    "Cache",
    "CachingResolver",
    "Lru",
    "S3Fifo",
    "Sieve",
]


class Cache(Protocol):
    """Cache abstract protocol. The :class:`CachingParser` will look
    values up, merge what was returned (possibly nothing) with what it
    got from its actual parser, and *re-set the result*.

    A :class:`Cache` is responsible for its own replacement policy.
    """

    @abc.abstractmethod
    def __setitem__(self, key: str, value: PartialParseResult) -> None:
        """Adds or replace ``value`` to the cache at key ``key``."""
        ...

    @abc.abstractmethod
    def __getitem__(self, key: str) -> Optional[PartialParseResult]:
        """Returns a partial result for ``key`` if there is any."""
        ...


class Lru:
    """Cache following a least-recently used replacement policy: when
    there is no more room in the cache, whichever entry was last seen
    the least recently is removed.

    Note that the cache size is adjusted after inserting the new
    entry, so the cache will temporarily contain ``maxsize + 1``
    items.

    Thread-safety: non-thread-safe, the upgrade of a key on hit fails
    if the key has already been removed, might also be possible for
    the capacity checking to become inconsistent or incorrect or
    incorrect on concurrent use e.g. if ``n`` threads try to set the
    same value (because they all got a cache miss and had to process
    the request) on a full cache of ``maxsize < n - 1``, they all set the
    value in the cache, check the cache size, and get a ``len() >
    maxsize``.

    This will lead to ``n`` calls to ``popitem``, which is more than
    the number of entries in the cache (``maxsize + 1``), and any
    excess call will trigger a ``KeyError``.

    """

    def __init__(self, maxsize: int):
        self.maxsize = maxsize
        self.cache: OrderedDict[str, PartialParseResult] = OrderedDict()
        self.lock = threading.Lock()

    def __getitem__(self, key: str) -> Optional[PartialParseResult]:
        with self.lock:
            e = self.cache.get(key)
            if e:
                self.cache.move_to_end(key)
            return e

    def __setitem__(self, key: str, value: PartialParseResult) -> None:
        with self.lock:
            self.cache[key] = value
            self.cache.move_to_end(key)
            while len(self.cache) > self.maxsize:
                self.cache.popitem(last=False)


@dataclasses.dataclass
class CacheEntry:
    __slots__ = ["key", "value", "freq"]
    key: str
    value: PartialParseResult
    freq: int


class S3Fifo:
    def __init__(self, maxsize: int):
        self.maxsize = maxsize
        self.index: Dict[str, Union[CacheEntry, str]] = {}
        self.small_target = max(1, int(maxsize / 10))
        self.small: Deque[CacheEntry] = deque()
        self.main_target = maxsize - self.small_target
        self.main: Deque[CacheEntry] = deque()
        self.ghost: Deque[str] = deque()
        self.lock = threading.Lock()

    def __getitem__(self, key: str) -> Optional[PartialParseResult]:
        e = self.index.get(key)
        if e and isinstance(e, CacheEntry):
            # small race here, we could bump the freq above the limit
            e.freq = min(e.freq + 1, 3)
            return e.value

        return None

    def __setitem__(self, key: str, r: PartialParseResult) -> None:
        with self.lock:
            if len(self.small) + len(self.main) >= self.maxsize:
                # if main is not overcapacity, resize small
                if len(self.main) < self.main_target:
                    self._evict_small()
                # evict_small could have moved every entry to main, in
                # which case we now need to evict from main
                if len(self.small) + len(self.main) >= self.maxsize:
                    self._evict_main()

            entry = CacheEntry(key, r, 0)
            if isinstance(self.index.get(key), str):
                self.main.appendleft(entry)
            else:
                self.small.appendleft(entry)
            self.index[key] = entry

    def _evict_main(self) -> None:
        while True:
            e = self.main.pop()
            if e.freq:
                e.freq -= 1
                self.main.appendleft(e)
            else:
                del self.index[e.key]
                return

    def _evict_small(self) -> None:
        while self.small:
            e = self.small.pop()
            if e.freq:
                e.freq = 0
                self.main.appendleft(e)
            else:
                g = self.index[e.key] = e.key
                self.ghost.appendleft(g)
                while len(self.ghost) > self.main_target:
                    g = self.ghost.pop()
                    if self.index.get(g) is g:
                        del self.index[g]
                return


@dataclasses.dataclass
class SieveNode:
    __slots__ = ("key", "value", "visited", "next")
    key: str
    value: PartialParseResult
    visited: bool
    next: Optional[SieveNode]


class Sieve:
    def __init__(self, maxsize: int) -> None:
        self.maxsize = maxsize
        self.cache: Dict[str, SieveNode] = {}
        self.head: Optional[SieveNode] = None
        self.tail: Optional[SieveNode] = None
        self.hand: Optional[SieveNode] = None
        self.prev: Optional[SieveNode] = None
        self.lock = threading.Lock()

    def __getitem__(self, key: str) -> Optional[PartialParseResult]:
        entry = self.cache.get(key)
        if entry:
            entry.visited = True
            return entry.value

        return None

    def __setitem__(self, key: str, value: PartialParseResult) -> None:
        with self.lock:
            if len(self.cache) >= self.maxsize:
                self._evict()

            node = self.cache[key] = SieveNode(key, value, False, None)
            if self.head:
                self.head.next = node
            self.head = node
            if self.tail is None:
                self.tail = node

    def _evict(self) -> None:
        obj: Optional[SieveNode]
        if self.hand:
            obj, pobj = self.hand, self.prev
        else:
            obj, pobj = self.tail, None

        while obj and obj.visited:
            obj.visited = False
            if obj.next:
                obj, pobj = obj.next, obj
            else:
                obj, pobj = self.tail, None

        if not obj:
            return

        self.hand = obj.next
        self.prev = pobj

        del self.cache[obj.key]
        if not obj.next:
            self.head = pobj

        if pobj:
            pobj.next = obj.next
        else:
            self.tail = obj.next


class Local:
    """Thread local cache decorator. Takes a cache factory and lazily
    instantiates a cache for each thread it's accessed from.

    This means the cache capacity and memory consumption is
    figuratively multiplied by however many threads the cache is used
    from, but those threads don't share their caching, and thus don't
    contend on cache use.

    """

    def __init__(self, factory: Callable[[], Cache]) -> None:
        self.cv: ContextVar[Cache] = ContextVar("local-cache")
        self.factory = factory

    @property
    def cache(self) -> Cache:
        c = self.cv.get(None)
        if c is None:
            c = self.factory()
            self.cv.set(c)
        return c

    def __getitem__(self, key: str) -> Optional[PartialParseResult]:
        return self.cache[key]

    def __setitem__(self, key: str, value: PartialParseResult) -> None:
        self.cache[key] = value


class CachingResolver:
    """A wrapping parser which takes an underlying concrete :class:`Cache`
    for the actual caching and cache strategy.

    The :class:`CachingParser` only interacts with the :class:`Cache`
    and delegates to the wrapped parser in case of lookup failure.

    :class:`CachingParser` will set entries back in the cache when
    filling them up, it does not update results in place (and can't
    really, they're immutable).
    """

    def __init__(self, parser: Resolver, cache: Cache):
        self.parser: Resolver = parser
        self.cache: Cache = cache

    def __call__(self, ua: str, domains: Domain, /) -> PartialParseResult:
        entry = self.cache[ua]
        if entry:
            if domains in entry.domains:
                return entry

            domains &= ~entry.domains

        r = self.parser(ua, domains)
        if entry:
            r = PartialParseResult(
                string=ua,
                domains=entry.domains | r.domains,
                user_agent=entry.user_agent or r.user_agent,
                os=entry.os or r.os,
                device=entry.device or r.device,
            )
        self.cache[ua] = r
        return r

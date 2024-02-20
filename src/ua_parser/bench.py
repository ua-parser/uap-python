import argparse
import csv
import io
import itertools
import sys
import time
from typing import Any, Callable, Iterable, List, Optional

from . import (
    BasicParser,
    CachingParser,
    Clearing,
    Locking,
    LRU,
    Matchers,
    Parser,
    load_builtins,
    load_yaml,
)
from .caching import Cache
from .re2 import Parser as Re2Parser
from .user_agent_parser import Parse

CACHEABLE = {
    "basic": True,
    "re2": True,
    "legacy": False,
}


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="ua_parser.bench",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="""\
Facility for benchmarking parsers against typical workloads.

Different sites and applications can have different traffic patterns, \
and thus want different setups and tradeoffs. This program allows \
testing ua-parser's different parsers, caches, and cache sizes against \
sample files in order to better match a system's needs and wants.

Also useful to bench the library itself.
""",
    )
    parser.add_argument(
        "file",
        type=argparse.FileType("r", encoding="utf-8"),
        help="""user agents file to benchmark on. The file must
        contain a user-agent per line, and can be as long as needed
        although longer files will take longer to benchmark on. Use
        `-` for stdin. """,
    )
    parser.add_argument(
        "-R",
        "--regexes",
        type=argparse.FileType("rb"),
        help="""Custom regexes.yaml file, if omitted the benchmark
will use the embedded regexes file from uap-core. Custom regexes files
allow testing new rules, or cut-down reference files if older rules
are not relevant to your needs, traffic, or analysis. Because YAML is
(mostly) a superset of JSON, JSON files should work fine.""",
    )
    parser.add_argument(
        "-O",
        "--output",
        choices=["stdout", "csv"],
        default="stdout",
        help="""By default, the result of each parser configuration /
        combination is printed to stdout with the parser name followed
        by the total parse time for the file, followed by the
        per-entry UA average. `csv` will instead output a valid CSV
        table, with a parser per column and a cache size per row.
        Parser configurations for which cache size is irrelevant will
        have the same value for every row.
        """,
    )
    parser.add_argument(
        "--parsers",
        nargs="+",
        choices=["basic", "re2", "legacy"],
        default=["basic", "re2", "legacy"],
        help="""Base parsers to benchmark. `basic` is a linear search
        through, `re2` is a prefiltered regex set implemented in C++,
        it is a lot faster and scales better but requires additional
        dependencies. `legacy` is the legacy API, which is essentially
        a basic parser with a clearing cache of a fixed 200 entries,
        but less layered so generally has a bit less overhead (~3%%).
        """,
    )
    parser.add_argument(
        "--caches",
        nargs="+",
        choices=["none", "clearing", "lru", "lru-threadsafe"],
        default=["none", "clearing", "lru", "lru-threadsafe"],
        help="""Cache implementations to test. `clearing` completely
        clears the cache to make room for new entries, `lru` uses a
        least-recently-used eviction policy. `lru` is not thread-safe
        so `lru-threadsafe` layers a lock atop it and measures
        *uncontended* locking overhead.
        """,
    )
    parser.add_argument(
        "--cachesizes",
        nargs="+",
        type=int,
        default=[10, 20, 50, 100, 200, 500, 1000, 2000, 5000],
        help="""Caches are a classic way to trade memory for
        performances. Different parsers and traffic patterns have
        different benefits from caches, this option allows testing the
        benefits of various cache sizes (and thus amounts of memory
        used) on the cache strategies or parsers.
        """,
    )
    args = parser.parse_args()

    if args.output == "stdout":
        run_stdout(args)
    elif args.output == "csv":
        run_csv(args)
    else:
        sys.exit(f"unknown output mode {args.output!r}")


def get_rules(parsers: List[str], regexes: Optional[io.IOBase]) -> Matchers:
    if regexes:
        if not load_yaml:
            sys.exit("yaml loading unavailable, please install pyyaml")

        rules = load_yaml(regexes)
        if "legacy" in parsers:
            print(
                "The legacy parser is incompatible with custom regexes, ignoring.",
                file=sys.stderr,
            )
            parsers.remove("legacy")
    else:
        rules = load_builtins()

    return rules


def run_stdout(args: argparse.Namespace) -> None:
    lines = list(args.file)
    count = len(lines)
    uniques = len(set(lines))
    print(f"{args.file.name}: {count} lines, {uniques} unique ({uniques/count:.0%})")

    rules = get_rules(args.parsers, args.regexes)

    for p, c, n in (
        (p, c, n)
        for p in args.parsers
        for c in (args.caches if CACHEABLE[p] and args.cachesizes != [0] else ["none"])
        for n in (args.cachesizes if c != "none" else [0])
    ):
        name = "-".join(map(str, filter(None, (p, c != "none" and c, n))))
        print(f"{name:30}", end=": ", flush=True)

        p = get_parser(p, c, n, rules)
        t = run(p, lines)

        secs = t / 1e9
        tpl = t / 1000 / len(lines)

        print(f"{secs:>3.2f}s ({tpl:>4.0f}us/line)")


def run_csv(args: argparse.Namespace) -> None:
    lines = list(args.file)
    LEN = len(lines) * 1000
    rules = get_rules(args.parsers, args.regexes)

    parsers = [
        (p, c, n)
        for p in args.parsers
        for c in (args.caches if CACHEABLE[p] else ["none"])
        for n in (args.cachesizes if c != "none" else [0])
    ]
    if not parsers:
        sys.exit("No parser selected")

    columns = {"size": ""}
    columns.update(
        (f"{p}-{c}", p if c == "none" else f"{p}-{c}")
        for p in args.parsers
        for c in (args.caches if CACHEABLE[p] else ["none"])
    )
    w = csv.DictWriter(sys.stdout, list(columns), dialect="unix")
    w.writerow(columns)

    parsers.sort(key=lambda t: t[2])
    grouped = itertools.groupby(parsers, key=lambda t: t[2])

    # these are the "template rows", which contain the no-cache
    # runs which get replicated on every cachesize row
    zeroes = {}
    # if we have entries with no cache size, compute them first so
    # we can apply them to every cachesize
    if parsers[0][2] == 0:
        (_, ps) = next(grouped)
        # cache could be ignored as it should always be `"none"`
        for parser, cache, _ in ps:
            p = get_parser(parser, cache, 0, rules)
            zeroes[f"{parser}-{cache}"] = run(p, lines) // LEN

    # special cases for configurations where we can't have
    # cachesize lines, write the template row out directly
    if args.parsers == ["legacy"] or args.caches == ["none"] or args.cachesizes == [0]:
        zeroes["size"] = 0
        w.writerow(zeroes)
        return

    for cachesize, ps in grouped:
        row = dict(zeroes, size=cachesize)
        for parser, cache, _ in ps:
            p = get_parser(parser, cache, cachesize, rules)
            row[f"{parser}-{cache}"] = run(p, lines) // LEN
        w.writerow(row)


def get_parser(
    parser: str, cache: str, cachesize: int, rules: Matchers
) -> Callable[[str], Any]:
    p: Parser
    if parser == "legacy":
        return Parse
    elif parser == "basic":
        p = BasicParser(rules)
    elif parser == "re2":
        p = Re2Parser(rules)
    else:
        sys.exit(f"unknown parser {parser!r}")

    c: Callable[[int], Cache]
    if cache == "none":
        return p.parse
    elif cache == "clearing":
        c = Clearing
    elif cache == "lru":
        c = LRU
    elif cache == "lru-threadsafe":
        c = lambda size: Locking(LRU(size))  # noqa: E731
    else:
        sys.exit(f"unknown cache algorithm {cache!r}")

    return CachingParser(p, c(cachesize)).parse


def run(
    parse: Callable[[str], None],
    lines: Iterable[str],
) -> int:
    t = time.perf_counter_ns()
    for line in lines:
        parse(line)
    return time.perf_counter_ns() - t


if __name__ == "__main__":
    main()
    sys.exit(0)

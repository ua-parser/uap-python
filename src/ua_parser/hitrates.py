import argparse
import itertools

from . import (
    CachingParser,
    Clearing,
    Domain,
    LRU,
    Parser,
    PartialParseResult,
)


class Noop(Parser):
    def __call__(self, ua: str, domains: Domain, /) -> PartialParseResult:
        return PartialParseResult(
            domains=domains,
            string=ua,
            user_agent=None,
            os=None,
            device=None,
        )


class Counter(Parser):
    def __init__(self, parser: Parser) -> None:
        self.count = 0
        self.parser = parser

    def __call__(self, ua: str, domains: Domain, /) -> PartialParseResult:
        self.count += 1
        return self.parser(ua, domains)


def main() -> None:
    ap = argparse.ArgumentParser(
        prog="ua_parser.hitrates",
        description="Measure hitrates of cache algorithms and sizes on sample file.",
    )
    ap.add_argument(
        "file",
        type=argparse.FileType("r", encoding="utf-8"),
        help="""User agents file to benchmark on. The file must
        contain a user agent per line. Use `-` for stdin.""",
    )
    ap.add_argument(
        "--cachesizes",
        nargs="+",
        type=int,
        default=[10, 20, 50, 100, 200, 500, 1000, 2000, 5000],
        help="""List of cache sizes to test hitrates for, for each
        cache algorithm. """,
    )

    args = ap.parse_args()

    lines = list(args.file)
    total = len(lines)
    uniques = len(set(lines))
    print(total, "lines", uniques, "uniques")
    print(f"ideal hit rate: {(total - uniques)/total:.0%}")
    print()
    for cache, cache_size in itertools.product(
        [Clearing, LRU],
        args.cachesizes,
    ):
        misses = Counter(Noop())
        parser = CachingParser(misses, cache(cache_size))
        for line in lines:
            parser.parse(line)

        print(
            f"{cache.__name__.lower()}({cache_size}): {(total - misses.count)/total:.0%} hit rate"
        )


if __name__ == "__main__":
    main()

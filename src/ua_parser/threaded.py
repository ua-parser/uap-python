import argparse
import itertools
import os
import random
import threading
import time
from typing import Iterable

from . import (
    load_builtins,
    BasicParser,
    CachingParser,
    Clearing,
    Domain,
    Locking,
    LRU,
    Parser,
)
from .re2 import Parser as Re2Parser


def worker(
    start: threading.Event,
    parser: Parser,
    lines: Iterable[str],
    end: threading.Barrier,
) -> None:
    start.wait()

    for ua in lines:
        parser.parse(ua)

    end.wait()


CACHESIZE = 1000


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
        "-n",
        "--threads",
        type=int,
        default=os.cpu_count() or 1,
    )
    args = ap.parse_args()

    lines = list(args.file)
    basic = BasicParser(load_builtins())
    for name, parser in [
        ("clearing", CachingParser(basic, Clearing(CACHESIZE))),
        ("LRU", CachingParser(basic, Locking(LRU(CACHESIZE)))),
        ("re2", Re2Parser(load_builtins())),
    ]:
        # randomize the dataset for each thread, predictably, to
        # simulate distributed load (not great but better than
        # nothing, and probably better than reusing the exact same
        # load)
        r = random.Random(42)
        start = threading.Event()
        end = threading.Barrier(args.threads + 1)

        for _ in range(args.threads):
            threading.Thread(
                target=worker,
                args=(start, parser, r.sample(lines, len(lines)), end),
            ).start()

        st = time.perf_counter_ns()
        start.set()
        end.wait()

        # each thread gets len(lines), so total number of processed
        # lines is t*len(lines)
        totlines = len(lines) * args.threads
        # runtime in us
        t = (time.perf_counter_ns() - st) / 1000
        print(f"{name:10}: {t/totlines:>4.0f}us/line")


if __name__ == "__main__":
    main()

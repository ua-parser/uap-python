from ua_parser import Domain, Parser, PartialResult, Result


def resolver(s: str, d: Domain) -> PartialResult:
    return PartialResult(d, None, None, None, s)


def test_parser_utility() -> None:
    """Tests that ``Parser``'s methods to behave as procedural
    helpers, for users who may not wish to instantiate a parser or
    something.

    """

    r = Parser.parse(resolver, "a")
    assert r == Result(None, None, None, "a")

    os = Parser.parse_os(resolver, "a")
    assert os is None

from ua_parser import Parser, ParseResult, PartialParseResult


def test_parser_utility() -> None:
    """Tests that ``Parser``'s methods to behave as procedural
    helpers, for users who may not wish to instantiate a parser or
    something.

    Sadly the typing doesn't really play nicely with that.

    """
    r = Parser.parse(lambda s, d: PartialParseResult(d, None, None, None, s), "a")  # type: ignore
    assert r == ParseResult(None, None, None, "a")

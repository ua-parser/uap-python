import re
from typing import Match, Optional


def get(m: Match[str], idx: int) -> Optional[str]:
    return (m[idx] or None) if 0 < idx <= m.re.groups else None


def replacer(repl: str, m: Match[str]) -> Optional[str]:
    """The replacement rules are frustratingly subtle and innimical to
    standard python fallback semantics:

    - if there is a non-null replacement pattern, then it must be used with
      match groups as template parameters (at indices 1+)
      - the result is stripped
      - if it is an empty string, then it's replaced by a null
    - otherwise fallback to a (possibly optional) match group
    - or null (device brand has no fallback)

    Replacement rules only apply to OS and Device matchers, the UA
    matcher has bespoke replacement semantics for the family (just
    $1), and no replacement for the other fields, either there is a
    static replacement or it falls back to the corresponding
    (optional) match group.

    """
    if not repl:
        return None

    return re.sub(r"\$(\d)", lambda n: get(m, int(n[1])) or "", repl).strip() or None

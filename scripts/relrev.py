import argparse
import contextlib
import hashlib
import json
import re
import shutil
import sys
import tempfile
import zipfile
from urllib import parse, request

parser = argparse.ArgumentParser(
    description="Retrieves the revision for the latest release of ua-parser-builtins",
)
parser.add_argument(
    "--domain",
    default="pypi.org",
)
args = parser.parse_args()

url = parse.urlunsplit(("https", args.domain, "simple/ua-parser-builtins", "", ""))

print("checking", url, file=sys.stderr)
res = request.urlopen(
    request.Request(
        url,
        headers={
            "Accept": "application/vnd.pypi.simple.v1+json",
        },
    )
)
if res.status != 200:
    exit(f"Failed to retrieve project distributions: {res.status}")

distributions = json.load(res)
version, distribution = next(
    (v, d)
    for v, d in zip(
        reversed(distributions["versions"]), reversed(distributions["files"])
    )
    if not d["yanked"]
    if re.fullmatch(
        r"(\d+!)?\d+(\.\d+)*(\.post\d+)?",
        v,
        flags=re.ASCII,
    )
)
print("latest version:", version, file=sys.stderr)

res = request.urlopen(distribution["url"])
if res.status != 200:
    exit(f"Failed to retrieve wheel: {res.status}")

with tempfile.SpooledTemporaryFile(256 * 1024) as tf:
    shutil.copyfileobj(res, tf)
    for name, val in distribution["hashes"].items():
        tf.seek(0)
        d = hashlib.file_digest(tf, name).hexdigest()
        if d != val:
            exit(f"{name} mismatch: expected {val!r} got {d!r}")
    tf.seek(0)
    with zipfile.ZipFile(tf) as z:
        # if the REVISION file is not found then it's fine it's a
        # pre-calver release (hopefully) and that means we should cut
        # a calver one
        with contextlib.suppress(KeyError):
            print(z.read("REVISION").decode())

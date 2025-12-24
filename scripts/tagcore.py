import argparse
import datetime
import pathlib
import shutil
import subprocess

CORE_REMOTE = "https://github.com/ua-parser/uap-core"


parser = argparse.ArgumentParser(
    description="""Updates `uap-core` to `ref` and tags it with `version`

If successful, writes the commit to `REVISION` and prints it to stdout.
"""
)
parser.add_argument(
    "--ref",
    default="HEAD",
    help="uap-core ref to build, defaults to HEAD (the head of the default branch)",
)
parser.add_argument(
    "--version",
    help="version to tag the package as, defaults to an YMD calendar version matching the ref's commit date",
)
args = parser.parse_args()


if not shutil.which("git"):
    exit("git required")

r = subprocess.run(
    ["git", "ls-remote", CORE_REMOTE, args.ref],
    encoding="utf-8",
    stdout=subprocess.PIPE,
)
if r.returncode:
    exit("Unable to query uap-core repo")

if r.stdout:
    if r.stdout.count("\n") > 1:
        exit(f"Found multiple matching refs for {args.ref}:\n{r.stdout}")
    commit, _rest = r.stdout.split("\t", 1)
else:
    try:
        int(args.ref, 16)
        commit = args.ref
    except ValueError:
        exit(f"Unknown or invalid ref {args.ref!r}")

CORE_PATH = pathlib.Path(__file__).resolve().parent.parent / "uap-core"

r = subprocess.run(["git", "-C", CORE_PATH, "fetch", CORE_REMOTE, commit])
if r.returncode:
    exit(f"Unable to retrieve commit {commit!r}")

if args.version:
    tagname = args.version
else:
    r = subprocess.run(
        ["git", "-C", CORE_PATH, "show", "-s", "--format=%cs", commit],
        encoding="utf-8",
        stdout=subprocess.PIPE,
    )
    if r.returncode or not r.stdout:
        exit(f"Unable to retrieve commit date from commit {commit!r}")

    tagname = datetime.date.fromisoformat(r.stdout.rstrip()).strftime("%Y%m%d")

subprocess.run(["git", "-C", CORE_PATH, "switch", "-d", commit])
subprocess.run(["git", "-C", CORE_PATH, "tag", tagname, commit])
CORE_PATH.joinpath("REVISION").write_text(commit)
print(commit)

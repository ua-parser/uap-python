import itertools
import json

# fmt: off
PYTHON_VERSIONS = [
    "3.10", "3.11", "3.12", "3.13", "3.14", "3.15",
    "3.14t", "3.15t",
    "pypy-3.11", "pypy-3.12",
    "graalpy-25",
]
matrix = [
    d
    for d in map(dict, itertools.product(
        (("python-version", v) for v in PYTHON_VERSIONS),
        (("arch", a) for a in ["x86_64", "aarch64"]),
        (("platform", p) for p in ["linux", "windows", "macos"]),
    ))
    # on windows, only cpython has arm builds (?)
    if (d["python-version"].startswith("3.") and d["python-version"] != "3.10")
        or d["platform"] != "windows"
        or d["arch"] != "aarch64"
]
# fmt: on

RUNNERS = {
    ("linux", "x86_64"): "ubuntu-latest",
    ("linux", "aarch64"): "ubuntu-24.04-arm",
    ("musllinux", "x86_64"): "ubuntu-latest",
    ("musllinux", "aarch64"): "ubuntu-24.04-arm",
    ("macos", "x86_64"): "macos-15-intel",
    ("macos", "aarch64"): "macos-latest",
    ("windows", "x86_64"): "windows-latest",
    ("windows", "aarch64"): "windows-11-arm",
}
for job in matrix:
    job["opts"] = ""
    job["runner"] = RUNNERS[job["platform"], job["arch"]]

    match job["python-version"]:
        case "3.14t":
            job["wheel"] = "3.14t"
        case "3.15t":
            job["wheel"] = "3.15"
        case v if v.startswith("3."):
            job["wheel"] = "3.14"
        case v:  # pypy, graal only do single-version wheels
            job["wheel"] = v
            if v.startswith("graal"):
                job["opts"] = "--experimental-options --engine.CompileOnly='~tregex re'"

print(json.dumps({"include": matrix}))

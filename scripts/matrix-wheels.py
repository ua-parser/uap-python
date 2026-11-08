import itertools
import json

builder = {
    ("linux", "x86_64"): "ubuntu-latest",
    ("linux", "aarch64"): "ubuntu-24.04-arm",
    ("musllinux", "x86_64"): "ubuntu-latest",
    ("musllinux", "aarch64"): "ubuntu-24.04-arm",
    ("macos", "x86_64"): "macos-15-intel",
    ("macos", "aarch64"): "macos-latest",
    ("windows", "x86_64"): "windows-latest",
    ("windows", "aarch64"): "windows-11-arm",
}

# fmt: off
matrix = [
    d
    for d in map(dict, itertools.product(
        (("python-version", v) for v in ["3.14", "3.14t", "3.15", "pypy-3.11", "pypy-3.12", "graalpy-25"]),
        (("arch", a) for a in ["x86_64", "aarch64"]),
        (("platform", p) for p in ["linux", "musllinux", "windows", "macos"]),
    ))
    # on windows, only cpython has arm builds (?)
    if d["python-version"].startswith("3.")
        or d["platform"] != "windows"
        or d["arch"] != "aarch64"
]
# fmt: on
# platform-specific fixups
for job in matrix:
    match job["platform"]:
        case "linux":
            job["manylinux"] = "auto"
            # use zig instead of docker for manylinux cross-builds (see #315)
            job["args"] = " --zig"
        case "mussllinux":
            job["manylinux"] = "musllinux_1_2"
        # windows/arm doesn't have a rust toolchain by default
        case "windows" if job["arch"] == "aarch64":
            job["setup-rust"] = True

    job["runs"] = builder[job["platform"], job["arch"]]

print(json.dumps({"include": matrix}))

"""
run python3 uap-core-changelog.py > uap-core-changelog.md
"""
import subprocess


def main():
    print("# uap-core (upstream) changelog")
    print(
        "In this document, "
        "we provide a link to compare the upstream change "
        "between each uap-python release."
    )
    tags = subprocess.check_output(["git", "tag"]).decode().strip().split("\n")
    tags.reverse()
    for new, old in zip(tags[:-1], tags[1:]):
        print("## from %s to %s:" % (old, new))
        diff = (
            subprocess.check_output(["git", "diff", old, new, "uap-core"])
            .decode()
            .strip()
            .split("\n")
        )
        old_commit, new_commit = [
            x.split(" ")[-1] for x in diff if "Subproject commit" in x
        ]
        print(
            "[click to check the change]"
            "(https://github.com/ua-parser/uap-core/compare/%s...%s)"
            % (old_commit, new_commit)
        )


if __name__ == "__main__":
    main()

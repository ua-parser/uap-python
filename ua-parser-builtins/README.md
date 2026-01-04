# Precompiled ruleset for [ua-parser]

This project does not do anything on its own, nor does it have any
actual API: it contains the dataset of [uap-core] pre-compiled for use
by [ua-parser] to decrease
initialisation times.

The precompiled ruleset is released monthly based on whatever
[uap-core]'s default branch is at that moment. The [uap-core] commit
used for creating the compiled ruleset is stored in the `REVISION`
file at the root of the wheel.

[ua-parser]: https://pypi.org/project/ua-parser/
[uap-core]: https://github.com/ua-parser/uap-core

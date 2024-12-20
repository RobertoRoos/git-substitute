# Git Substitute

[![PyPI](https://img.shields.io/pypi/v/git-substitute)](https://pypi.org/project/git-substitute/)
[![tests](https://github.com/RobertoRoos/git-substitute/actions/workflows/tests.yml/badge.svg)](https://github.com/RobertoRoos/git-substitute/actions)

This repository contains a basic tool to generate files with Git information through templates.
A typical application could be embedding Git version info in source code right before compilation 

## Installing

Install with `pip install git-substitute`.

Or from a local clone, run `poetry install` or `pip install . [-e]`.
You could also install directly from git with `pip install https://github.com/RobertoRoos/git-substitute`.

## How to use

### Commands

Run as either `git_substitute ...` or `python -m git_substitute ...`.

Typical usage: `git_substitute current_version_template.cs`.
This will copy the template file, substitute Git variables and commands and create a new file with a similar name, but without `_template` in the name.

See `git_substitute --help` for all options.

### Templates

Use `{{...}}` in template file for placeholders.
There are types of content: variables and direct Git function calls.

Variables are in uppercase with underscores, and start with `GIT_`.
E.g.: `{{GIT_TAG}}`.

Instead of predefined variables you could use direct calls to Git.
These are lowercase and start with `git ...`.
E.g. `{{git refname --dirty}}`.  
Note that the interface through GitPython is used, instead of opening a shell directly.

### Variables

In case you are not sure what information to embed, use `GIT_DESCRIPTION_DIRTY` as it is very concise and clear. 

| Placeholder           | Description                                                                                                     | Example                                  |
|-----------------------|-----------------------------------------------------------------------------------------------------------------|------------------------------------------|
| GIT_HASH              | Full hash of the last commit                                                                                    | 4cc498b3c37375d8d9138fdab553ced012cafc7a |
| GIT_HASH_SHORT        | 8-char hash of the last commit                                                                                  | 4cc498b3                                 |
| GIT_DATE              | Datetime of the last commit                                                                                     | 17-12-2024 12:47:10                      |
| GIT_NOW               | The current date and time, not a git command at all                                                             | 19-12-2024 16:20:35                      |
| GIT_TAG               | Most relevant tag (result of `git tag`)                                                                         | v1.0.0                                   |
| GIT_BRANCH            | Current branch name                                                                                             | master                                   |
| GIT_DESCRIPTION       | Most relevant tag + number of commits since then + last commit  (result of `git describe --tags --always`)      | v0.0.1-1-g4cc498b                        |
| GIT_DESCRIPTION_DIRTY | Same as `GIT_DESCRIPTION`, except it also adds the `--dirty` argument to mark if there were uncommitted changes | v0.0.1-1-g4cc498b-dirty                  |
| GIT_DIRTY             | `1` if there are uncommited chances, otherwise `0`                                                              | 0                                        |

To use literal placeholder symbols in your template, escape them with a backslash: `\{\{` and `\}\}`.

### Example

```c++
// File: src/version_template.cpp

#include <string>

// Specificy the version for this library
const std::string version = "{{GIT_DESCRIPTION_DIRTY}}";
```

Then in your build script you may have a step like:
```shell
git_substitute src/version_template.cpp
```

Which will create `src/version.cpp` and can be compiled into your application.

## How to develop

Install with development dependencies with `poetry install --with dev`.

[Poetry Dynamic Versioning](https://pypi.org/project/poetry-dynamic-versioning/) is used for automatic version detection.

### How to publish

The package is published to PyPi, at https://pypi.org/project/git-substitute/.

Publishing is now done manually, through `poetry build` and `poetry publish`.

# Git Substitute

This repository contains a basic tool to generate files with Git information through templates.

## Installing

From a local clone, run `poetry install` or `pip install . [-e]`.

You can also install directly from git with `pip install https://github.com/RobertoRoos/git-substitute`.

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
| GIT_TAG               | Most relevant tag (result of `git tag`)                                                                         | v1.0.0                                   |
| GIT_BRANCH            | Current branch name                                                                                             | master                                   |
| GIT_DESCRIPTION       | Most relevant tag + number of commits since then + last commit  (result of `git describe --tags --always`)      | v0.0.1-1-g4cc498b                        |
| GIT_DESCRIPTION_DIRTY | Same as `GIT_DESCRIPTION`, except it also adds the `--dirty` argument to mark if there were uncommitted changes | v0.0.1-1-g4cc498b-dirty                  |

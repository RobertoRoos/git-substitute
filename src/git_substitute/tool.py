from __future__ import annotations

import logging
import re
import sys
from argparse import ArgumentParser
from datetime import datetime
from pathlib import Path

from git import Repo

from . import __version__

logger = logging.getLogger("git_substitute")


class SubstituteTool:
    """Tool to perform Git info substitution.

    Class can be instantiated normally but is made to run with system arguments.
    ``argparse`` is done in the constructor.
    """

    EMPTY = "[empty]"
    DATETIME_FORMAT = "%d-%m-%Y %H:%M:%S"

    def __init__(self, *args):
        """Pass e.g. ``sys.args[1:]`` (skipping the script part of the arguments)."""

        parser = ArgumentParser(
            description="Generate files with information from Git, based on templates."
        )

        parser.add_argument(
            "template",
            help="Path to the template file. If this filename ends with `_template`, `_Template` or `Template`, and no other options are supplied, the output will be a similar file without this suffix.",
        )
        group = parser.add_mutually_exclusive_group()
        group.add_argument("--output", "-o", help="Output is saved to this file")
        group.add_argument(
            "--stdout",
            default=False,
            action="store_true",
            help="Echo result to the terminal instead",
        )
        parser.add_argument(
            "--repo",
            "-r",
            help="Set explicit root to Git repository (by default, start searching for current directory)",
        )
        parser.add_argument(
            "--verbose",
            "-v",
            default=False,
            action="store_true",
            help="Print information to the terminal",
        )
        parser.add_argument(
            "--quiet",
            "-q",
            default=False,
            action="store_true",
            help="Print logs to stderr instead of stdout",
        )
        parser.add_argument(
            "--version", "-V", action="version", version="%(prog)s " + __version__
        )

        self.args = parser.parse_args(*args)
        self.repo: Repo | None = None
        self.is_empty: bool = False  # True if there is not a single commit

        # Adjust logger:
        if self.args.verbose:
            logger.setLevel(logging.DEBUG)
        if self.args.quiet:
            logging.basicConfig(stream=sys.stderr)

    def run(self) -> int:
        self.repo = Repo(self.args.repo)
        logger.debug("Using Git directory: " + self.repo.common_dir)

        # Check if repo is entirely emtpy:
        try:
            _ = self.repo.head.object
        except ValueError:
            logger.warning("Git repository is entirely empty")
            self.is_empty = True

        template_file = Path(self.args.template).absolute()
        logger.debug(f"Using template file: {template_file}")

        template_content = template_file.read_text()

        # Perform placeholder substitution:
        re_keyword = re.compile(r"{{([^}]+)}}")
        new_content, substitutions = re_keyword.subn(
            self._keyword_replace, template_content
        )

        # Now fix escaped characters:
        new_content = new_content.replace(r"\{\{", "{{").replace(r"\}\}", "}}")

        if self.args.stdout:
            print(new_content, end="")
            return 0

        if self.args.output:
            target_file = Path(self.args.output)
        else:
            target_file = self._deduce_target_file(template_file)

        logger.debug(f"Going to write to: {target_file}")

        written = target_file.write_text(new_content)
        if written == 0:
            logger.warning(f"Failed to write anything to {target_file}")
            return 255  # Error

        logger.debug(f"Successfully written {written} bytes")

        return 0  # Ok

    def _keyword_replace(self, match) -> str:
        """Callback for regex replacement."""
        keyword: str = match.group(1)  # Skipping the "{{" and "}}"

        if keyword.startswith("GIT_"):
            # Get value through local property
            if self.is_empty:
                return self.EMPTY
            return getattr(self, keyword.lower())

        if keyword.startswith("git "):
            # Run function instead
            commands_str = keyword[4:]  # Strip "git "
            commands = commands_str.split(" ")
            func = getattr(self.repo.git, commands[0])  # Retrieve function handle
            return func(*commands[1:])  # Call, passing in remaining words as arguments

        raise ValueError(f"Unrecognized class of placeholder: {keyword}")

    @staticmethod
    def _deduce_target_file(template: Path) -> Path:
        """Guess a target file, based on the template path."""
        name = template.name
        remove = ["_template", "Template", "TEMPLATE"]
        for r in remove:
            name = name.replace(r, "")

        if name == template.name:
            raise ValueError(
                f"Failed to deduce a target name from the file `{template.name}`. Use the `--output` flag or make sure your template file ends with `_?[Tt]emplate`."
            )

        return template.parent / name

    @property
    def git_hash(self) -> str:
        return self.repo.head.object.hexsha

    @property
    def git_hash_short(self) -> str:
        return self.git_hash[:8]

    @property
    def git_date(self) -> str:
        return self.repo.head.object.committed_datetime.strftime(self.DATETIME_FORMAT)

    @property
    def git_now(self) -> str:
        return datetime.now().strftime(self.DATETIME_FORMAT)

    @property
    def git_tag(self) -> str:
        # Getting the most relevant tag through `self.repo` is not so straightforward
        # Easier to just use the `git tag` command directly
        return self.repo.git.tag()

    @property
    def git_version(self) -> str:
        tag = self.repo.git.tag()
        re_version = re.compile(r"\d+\.\d+\.+\d+")
        match = re_version.search(tag)
        if not match:
            logger.warning(
                f"Failed to determine version from {tag}, continuing with 0.0.0"
            )
            return "0.0.0"

        return match.group()

    @property
    def git_branch(self) -> str:
        return self.repo.active_branch.name

    @property
    def git_description(self):
        return self.repo.git.describe("--tags", "--always")

    @property
    def git_description_dirty(self):
        return self.repo.git.describe("--tags", "--always", "--dirty")

    @property
    def git_dirty(self) -> str:
        return "1" if self.repo.is_dirty() else "0"

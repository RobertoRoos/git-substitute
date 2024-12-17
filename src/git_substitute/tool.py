from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path
import re

from git import Repo


class SubstituteTool:
    """Tool to perform Git info substitution.

    Class can be instantiated normally but is made to run with system arguments.
    ``argparse`` is done in the constructor.
    """

    def __init__(self, *args):
        """Pass e.g. ``sys.args[1:]`` (skipping the script part of the arguments)."""

        parser = ArgumentParser(
            description="Generate files with information from Git, based on templates."
        )

        parser.add_argument("template", help="Path to the template file")
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

        self.args = parser.parse_args(*args)
        self.repo: Repo | None = None

    def run(self) -> int:
        self.repo = Repo(self.args.repo)

        template_file = Path(self.args.template).absolute()

        template_content = template_file.read_text()

        re_keyword = re.compile(r"{{([^}]+)}}")
        new_content, substitutions = re_keyword.subn(self._keyword_repl, template_content)

        if self.args.stdout:
            print(new_content, end="")

        return 0

    def _keyword_repl(self, match) -> str:
        """Callback for regex replacement."""
        keyword: str = match.group(1)  # Skipping the "{{" and "}}"
        return ""

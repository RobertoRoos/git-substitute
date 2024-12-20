from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from git_substitute.tool import SubstituteTool


class TestCLI:
    """Test the CLI interface, not so much detailed function.

    If the basics work, we'll assume the CLI wors and we can test the class directly
    instead.
    """

    def test_help(self):

        # Re-use the current executable to call our tool from a new process:
        result = subprocess.run(
            [sys.executable, "-m", "git_substitute", "--help"], capture_output=True
        )
        assert result.returncode == 0

        txt = result.stdout.decode()
        assert "usage:" in txt
        assert "Generate files with information from Git" in txt


class TestSubstitute:
    """Test functionality.

    The git repository of this project is used for Git info. This makes for a fixture
    that is not static, but it is easy.
    """

    tmp_path: Path | None = None

    DATA = Path(__file__).parent / "data"

    @pytest.fixture(autouse=True)
    def _data_files(self, tmp_path, monkeypatch):
        """Fixture to copy all fixture files into a temp dir."""
        self.tmp_path = tmp_path / "data"
        shutil.copytree(self.DATA, self.tmp_path)
        monkeypatch.chdir(self.tmp_path)  # Fake as current working directory

    def test_variables(self):
        this_repo = self.DATA.parent.parent
        tool = SubstituteTool(["variables_template.cpp", "--repo", str(this_repo)])
        assert tool.run() == 0

        new_file = self.tmp_path / "variables.cpp"
        assert new_file.exists()

        new_content = new_file.read_text()
        assert "{{" not in new_content and "}}" not in new_content

    def test_commands(self):
        this_repo = self.DATA.parent.parent
        tool = SubstituteTool(["commands_template.cpp", "--repo", str(this_repo)])
        assert tool.run() == 0

        new_file = self.tmp_path / "commands.cpp"
        assert new_file.exists()

        new_content = new_file.read_text()
        assert "{{" not in new_content and "}}" not in new_content

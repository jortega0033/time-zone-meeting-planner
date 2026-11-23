"""Scaffold smoke tests: modules import, help and version work, a stub exits non-zero."""

import importlib
import io
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import oracle  # noqa: F401  (tests/oracle.py, imports nothing from the package)
from meeting_planner import __version__
from meeting_planner.cli import main

MODULES = ["zones", "schema", "calendars", "options", "solver", "storage", "server", "cli"]


class ModuleSmoke(unittest.TestCase):
    def test_modules_import(self):
        for name in MODULES:
            with self.subTest(module=name):
                importlib.import_module(f"meeting_planner.{name}")

    def test_static_tokens_exist(self):
        root = Path(__file__).resolve().parent.parent
        self.assertTrue((root / "meeting_planner" / "static" / "tokens.css").is_file())


class CliSmoke(unittest.TestCase):
    def run_cli(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            try:
                code = main(list(argv))
            except SystemExit as exc:
                code = exc.code
        return code, out.getvalue(), err.getvalue()

    def test_help(self):
        code, out, _ = self.run_cli("--help")
        self.assertEqual(code, 0)
        self.assertIn("serve", out)

    def test_version(self):
        code, out, _ = self.run_cli("--version")
        self.assertEqual(code, 0)
        self.assertIn(__version__, out)

    def test_stub_not_implemented(self):
        code, _, err = self.run_cli("solve", "x.json")
        self.assertNotEqual(code, 0)
        self.assertIn("not implemented yet: see #4", err)


if __name__ == "__main__":
    unittest.main()

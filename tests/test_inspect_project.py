"""Contract checks: bounded discovery must not expose lock URL credentials."""

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


SKILL = Path(__file__).resolve().parents[1] / "skills" / "nix-toolbox"
SPEC = importlib.util.spec_from_file_location("inspector", SKILL / "scripts" / "inspect_project.py")
inspector = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(inspector)


class InspectorContract(unittest.TestCase):
    def test_lock_metadata_omits_urls_and_never_evaluates(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            lock = root / "flake.lock"
            lock.write_text(json.dumps({"nodes": {"input": {"locked": {
                "type": "git", "rev": "123", "url": "https://user:secret@example.invalid/repo"
            }}}}))
            before = lock.read_bytes()
            with patch.object(inspector.shutil, "which", return_value=None), \
                    patch.object(inspector.subprocess, "run") as run:
                data = inspector.inspect(root)
            run.assert_not_called()
            self.assertFalse(data["nix"]["available"])
            self.assertFalse(data["project_evaluated"])
            self.assertNotIn("secret", json.dumps(data))
            self.assertEqual(data["locked_inputs"]["input"]["rev"], "123")
            self.assertEqual(before, lock.read_bytes())

    def test_malformed_and_external_symlink_locks_are_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "project"
            root.mkdir()
            lock = root / "flake.lock"
            lock.write_text("invalid-json")
            with patch.object(inspector.shutil, "which", return_value=None):
                self.assertIn("lock_error", inspector.inspect(root))
            lock.unlink()
            external = Path(directory) / "external"
            external.write_text('{"sensitive": "do not read"}')
            lock.symlink_to(external)
            with patch.object(inspector.shutil, "which", return_value=None):
                data = inspector.inspect(root)
            self.assertIn("lock_error", data)
            self.assertNotIn("locked_inputs", data)


if __name__ == "__main__":
    unittest.main()

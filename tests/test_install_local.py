import importlib.util
from pathlib import Path
import tomllib
import unittest


SPEC = importlib.util.spec_from_file_location(
    "installer", Path(__file__).resolve().parents[1] / "scripts" / "install_local.py"
)
installer = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(installer)


class InstallerConfigContract(unittest.TestCase):
    def test_preserves_unrelated_settings_and_comments(self):
        original = b'# Keep this comment\nmodel = "existing-model"\n[mcp_servers.other]\nrequired = false\nargs = ["a", "b"]\n'
        updated = installer.add_server(original, "/some path/mcp-nixos")
        self.assertTrue(updated.startswith(original.rstrip()))
        parsed = tomllib.loads(updated.decode())
        self.assertEqual(parsed["model"], "existing-model")
        self.assertEqual(parsed["mcp_servers"]["other"]["args"], ["a", "b"])
        self.assertEqual(installer.add_server(updated, "/some path/mcp-nixos"), updated)

    def test_accepts_new_config_and_rejects_conflicting_server(self):
        updated = installer.add_server(b"", "/new/server")
        self.assertEqual(tomllib.loads(updated.decode())["mcp_servers"]["mcp-nixos"]["command"], "/new/server")
        with self.assertRaises(ValueError):
            installer.add_server(updated, "/different/server")
        disabled = b'[mcp_servers.mcp-nixos]\ncommand = "/new/server"\nenabled = false\n'
        with self.assertRaises(ValueError):
            installer.add_server(disabled, "/new/server")


if __name__ == "__main__":
    unittest.main()

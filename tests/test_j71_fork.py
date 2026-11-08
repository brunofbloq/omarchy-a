"""No-device checks for the research fork's boot guard and payload staging."""
import importlib.util
import os
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


common = module("j71_common", ROOT / "tools/j71/common.py")
preflight = module("j71_preflight", ROOT / "tools/j71/preflight.py")


class J71Guard(unittest.TestCase):
    def test_accepts_exact_j71_dfu(self):
        preflight.require_j71({"mode": "dfu", "chip": 0x8960, "board": 0x10}, common.pins()["target"])

    def test_refuses_cellular_same_soc_recovery_and_missing_identity(self):
        for device in (
            {"mode": "dfu", "chip": 0x8960, "board": 0x12},
            {"mode": "recovery", "chip": 0x8960, "board": 0x10},
            {"mode": "dfu", "chip": 0x8010, "board": 0x10},
            {"mode": "dfu", "chip": 0x8960},
        ):
            with self.subTest(device=device), self.assertRaises(ValueError):
                preflight.require_j71(device, common.pins()["target"])


class PayloadStaging(unittest.TestCase):
    def test_preserves_a_modified_project(self):
        with tempfile.TemporaryDirectory() as temporary:
            project = common.stage_payload(Path(temporary) / "ram")
            (project / "init").write_text("owner's changed experiment\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                common.stage_payload(project)
            self.assertEqual((project / "init").read_text(), "owner's changed experiment\n")

    @unittest.skipIf(os.name == "nt", "symlink creation requires special Windows privileges")
    def test_refuses_a_symlink_even_when_bytes_match(self):
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary) / "ram"
            project.mkdir()
            external = Path(temporary) / "owner-init"
            external.write_bytes((common.HERE / "payload/init").read_bytes())
            external.chmod(0o600)
            (project / "init").symlink_to(external)
            with self.assertRaises(ValueError):
                common.stage_payload(project)
            self.assertEqual(external.stat().st_mode & 0o777, 0o600)


if __name__ == "__main__":
    unittest.main()

import contextlib
import io
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from _common import save_manifest
import deliver


class DeliveryTests(unittest.TestCase):
    def test_noncommercial_flag_cannot_bypass_monetized_project(self):
        with tempfile.TemporaryDirectory() as folder:
            proj = Path(folder)
            save_manifest(proj, {"monetized": True, "assets": []})
            with patch.object(sys, "argv", ["deliver.py", str(proj), "--video", "unused.mp4", "--allow-noncommercial"]), \
                    patch.object(deliver, "need", return_value="ffmpeg"), \
                    contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as raised:
                deliver.main()
            self.assertEqual(raised.exception.code, 2)

    def test_missing_unknown_or_noncommercial_license_blocks(self):
        for license_ in ("", "CC-BY-NC 4.0", "uso comercial não verificado"):
            with self.subTest(license=license_):
                self.assertEqual(len(deliver.license_blockers({"assets": [{"license": license_, "commercial_ok": True}]})), 1)
        self.assertEqual(deliver.license_blockers({"assets": [{"license": "MIT", "commercial_ok": True}]}), [])


if __name__ == "__main__":
    unittest.main()

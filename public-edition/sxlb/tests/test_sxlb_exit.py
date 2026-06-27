import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from sxlb_exit import run_exit
from test_sxlb_guard import make_valid_case_package


class SxlbExitTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="sxlb-exit-"))

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir)

    def test_run_exit_requests_catalog_refresh_by_default(self):
        with patch("sxlb_exit.close_case") as close_case:
            close_case.return_value = {
                "guard": {"ok": True},
                "state": "已回奏",
                "catalog": {"ok": True},
            }

            result = run_exit(self.temp_dir)

        close_case.assert_called_once_with(
            self.temp_dir,
            phase="completion",
            refresh_catalog_after=True,
        )
        self.assertTrue(result["guard"]["ok"], result["guard"])
        self.assertEqual(result["state"], "已回奏")
        self.assertEqual(result["next_action"], "exit-confirmation")

    def test_run_exit_reports_blocked_when_guard_fails(self):
        make_valid_case_package(self.temp_dir)
        (self.temp_dir / "verification.md").write_text("# 验证矩阵\n", encoding="utf-8")

        result = run_exit(self.temp_dir)

        self.assertFalse(result["guard"]["ok"])
        self.assertEqual(result["state"], "待分流")
        self.assertEqual(result["next_action"], "repair-before-exit")
        self.assertTrue(result["guard"]["errors"])


if __name__ == "__main__":
    unittest.main()

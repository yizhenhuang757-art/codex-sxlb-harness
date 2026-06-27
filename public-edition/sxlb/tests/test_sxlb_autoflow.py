import shutil
import tempfile
import unittest
from pathlib import Path

from sxlb_autoflow import run_autoflow
from test_shangshu_dispatch import make_real_dispatch_case


class SxlbAutoflowTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="sxlb-autoflow-"))

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir)

    def test_blocks_non_allowlisted_stage(self) -> None:
        make_real_dispatch_case(self.temp_dir)
        dispatch = self.temp_dir / "dispatch-order.md"
        dispatch.write_text(
            dispatch.read_text(encoding="utf-8").replace("当前阶段：尚书派发", "当前阶段：中书拟制"),
            encoding="utf-8",
        )
        result = run_autoflow(self.temp_dir)
        self.assertFalse(result["ok"])
        self.assertEqual(result["state"], "blocked")

    def test_advances_allowlisted_stage(self) -> None:
        make_real_dispatch_case(self.temp_dir)
        result = run_autoflow(self.temp_dir)
        self.assertTrue(result["ok"])
        self.assertEqual(result["state"], "awaiting-returns")
        self.assertEqual(result["arrival_hooks"], [])


if __name__ == "__main__":
    unittest.main()

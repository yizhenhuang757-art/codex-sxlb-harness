import shutil
import tempfile
import unittest
from pathlib import Path

from sxlb_flow import advance_case
from test_menxia_review import make_review_case
from test_shangshu_dispatch import make_local_dispatch_case, make_real_dispatch_case


class SxlbFlowTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="sxlb-flow-"))

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir)

    def test_advancing_real_dispatch_prepares_packets_and_waits_for_returns(self) -> None:
        make_real_dispatch_case(self.temp_dir)
        result = advance_case(self.temp_dir, force=True)
        self.assertEqual(result["state"], "awaiting-returns")
        self.assertTrue((self.temp_dir / "subagents" / "manifest.json").exists())
        self.assertTrue((self.temp_dir / "shangshu-dispatch-summary.md").exists())
        self.assertEqual([action["action"] for action in result["actions"]], ["dispatch"])
        self.assertEqual(len(result["missing_returns"]), 2)
        self.assertEqual(result["arrival_hooks"], [])

    def test_advancing_complete_real_case_merges_and_reviews(self) -> None:
        make_review_case(self.temp_dir)
        (self.temp_dir / "menxia-review.md").unlink(missing_ok=True)
        (self.temp_dir / "subagents" / "merge-summary.md").unlink()
        result = advance_case(self.temp_dir, force=True)
        self.assertEqual(result["state"], "reviewed-pass")
        self.assertEqual([action["action"] for action in result["actions"]], ["dispatch", "merge", "review"])
        hook_names = [hook["hook"] for hook in result["arrival_hooks"]]
        self.assertIn("completion-precheck", hook_names)
        self.assertIn("records-routing-candidate", hook_names)
        self.assertTrue(all(hook["router_role"] == "index-only" for hook in result["arrival_hooks"]))
        self.assertTrue(all("owner_script" in hook for hook in result["arrival_hooks"]))
        self.assertTrue((self.temp_dir / "subagents" / "merge-summary.md").exists())
        review_text = (self.temp_dir / "menxia-review.md").read_text(encoding="utf-8")
        self.assertIn("结论：通过", review_text)
        ledger_text = (self.temp_dir / "event-ledger.md").read_text(encoding="utf-8")
        self.assertIn("动作：merge", ledger_text)

    def test_advancing_local_case_reviews_without_merge(self) -> None:
        make_local_dispatch_case(self.temp_dir)
        (self.temp_dir / "dispatch-order.md").write_text(
            (self.temp_dir / "dispatch-order.md").read_text(encoding="utf-8").replace("当前阶段：尚书派发", "当前阶段：门下复核"),
            encoding="utf-8",
        )
        (self.temp_dir / "zhongshu-plan.md").write_text(
            """# 中书方案

## 目标与边界

- 目标：Handle a local office case
- 不做什么：skip review
- 成功标准：review remains explicit

## 任务拆解

- 主任务：execute locally
- 子任务：review locally
- 风险与未知：none

## 双轨规划

- 文线：n/a
- 武线：n/a
- 合流规则：n/a

## 路由建议

- 任务类别：C
- 推荐链路：太子 -> 中书省 -> 门下省 -> 尚书省 -> 六部 -> 门下复核 -> 回奏
- 需要审议的问题：whether evidence is sufficient

## 技能与官署映射

- 主要官署：工部, 门下省
- 主要技能：python
- 额外技能：none
- 能力召回：family:sxlb-governance
""",
            encoding="utf-8",
        )
        (self.temp_dir / "memorial-report.md").write_text(
            """# 回奏

## 任务总结

- 任务：Handle a local office case
- 使用链路：太子 -> 中书省 -> 门下省 -> 尚书省 -> 六部 -> 门下复核 -> 回奏
- 当前结果：completed
- 停止原因：n/a
- 停止时状态：门下复核
- 门下复核依据：menxia-review.md

## 核心决策

- 关键决策：Local office work remained bounded
- 双轨合流：n/a

## 验证与风险

- 验证证据：manual verification completed
- 未完成/未验证项：none
- 剩余风险：minor residual integration risk

## 记录分流

- 案卷归档：$SXLB_CASE_ROOT/sxlb/test-local-flow
- 项目复盘：$SXLB_CASE_ROOT/sxlb/test-local-flow/retrospective.md
- canonical 更新：none
- restart 更新：none

## 复盘四问

- 顺的地方：local execution stayed simple
- 卡的地方：none
- 返工点：none
- 下次项目内应改进之处：keep using governed review

## 下一步建议

- 推荐动作：run final review
- 是否继续在 sxlb 中：yes
""",
            encoding="utf-8",
        )
        (self.temp_dir / "learning-candidates.jsonl").write_text(
            '{"type":"governance","scope":"project","source":"retrospective","confidence":6,"summary":"Keep local flow review explicit","promote_to":"none","stale_when":"sxlb flow protocol changes"}\n',
            encoding="utf-8",
        )
        (self.temp_dir / "artifact-registry.md").write_text(
            """# 产物注册表

| 产物 | 生成官署 | 状态 | 下游消费 | blocking |
|---|---|---|---|---|
| case.md | 太子 | reviewed | 中书省 | yes |
| zhongshu-plan.md | 中书省 | reviewed | 尚书省 | yes |
| dispatch-order.md | 尚书省 | reviewed | 门下省 | yes |
| menxia-review.md | 门下省 | reviewed | 礼部 | yes |
| memorial-report.md | 礼部 | reviewed | 回奏 | yes |
| event-ledger.md | 太子 | reviewed | 门下省 | yes |
| verification.md | 刑部 | reviewed | 门下省 | yes |
| learning-candidates.jsonl | 吏部 | reviewed | self-improving-agent | yes |
| menxia-readiness.md | 门下省 | reviewed | 门下复核 | yes |
| records-routing.md | 礼部 | reviewed | 待分流 | yes |
""",
            encoding="utf-8",
        )
        (self.temp_dir / "records-routing.md").write_text(
            """# 记录分流

## 分流决策

- canonical：none
- report-only：local-flow notes
- restart-update：none
- no-writeback：none
""",
            encoding="utf-8",
        )
        (self.temp_dir / "verification.md").write_text(
            """# 验证矩阵

## 验证概览

- 验证目标：local office completion
- 受影响对象：sxlb case package
- 验证结论：pass
- 行为断言/不变量：local office package remains guard-valid
- 测试有效性：manual verification would fail if required case artifacts were missing

## 验证证据

- 命令或动作：manual verification
- 结果：pass
- 失败项：none
- 复验：pass
- 未覆盖风险：minor residual integration risk
""",
            encoding="utf-8",
        )
        (self.temp_dir / "event-ledger.md").write_text(
            """# 事件簿

- 时间：2026-04-23T10:00:00
  状态：待立案
  动作：intake
  发起：太子
  摘要：Case opened
  证据：case.md

- 时间：2026-04-23T10:05:00
  状态：中书拟制
  动作：plan
  发起：中书省
  摘要：Plan drafted
  证据：zhongshu-plan.md

- 时间：2026-04-23T10:08:00
  状态：门下审议
  动作：review
  发起：门下省
  摘要：Dispatch approved
  证据：menxia-review.md

- 时间：2026-04-23T10:10:00
  状态：尚书派发
  动作：dispatch
  发起：尚书省
  摘要：Local order issued
  证据：dispatch-order.md

- 时间：2026-04-23T10:20:00
  状态：待回奏
  动作：memorial
  发起：礼部
  摘要：Memorial draft prepared
  证据：memorial-report.md
""",
            encoding="utf-8",
        )
        result = advance_case(self.temp_dir, force=True)
        self.assertEqual(result["state"], "reviewed-pass")
        self.assertEqual([action["action"] for action in result["actions"]], ["review"])
        self.assertIn("completion-precheck", [hook["hook"] for hook in result["arrival_hooks"]])
        self.assertFalse(result["merge_missing"])
        self.assertTrue((self.temp_dir / "menxia-review.md").exists())


if __name__ == "__main__":
    unittest.main()

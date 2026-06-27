import shutil
import tempfile
import unittest
from pathlib import Path

from menxia_review import run_completion_review


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def make_review_case(root: Path, *, verification_evidence: str = "unit tests and branch returns reviewed") -> None:
    write(
        root / "case.md",
        """# 立案单

## 基本信息

- 任务：Review a governed case
- 用户目标：Only allow memorialization with complete evidence
- 约束：Keep the review explicit
- 风险级别：medium
- 案卷路径：$SXLB_CASE_ROOT/sxlb/test-review-case
- restart 目标：n/a
- 能力召回：family:sxlb-governance

## 任务分类

- 任务类别：C
- 最小合法链路：太子 -> 尚书省 -> 单部执行 -> 门下复核 -> 回奏
- 当前建议链路：太子 -> 中书省 -> 门下省 -> 尚书省 -> 六部 -> 门下复核 -> 回奏
- 首办官署：门下省
- 下一站：门下省

## 立案备注

- 关键未知：none
- 需要用户确认：no
- 可能更新的 canonical：none
""",
    )
    write(
        root / "dispatch-order.md",
        """# 派令

## 派发信息

- 当前阶段：尚书派发
- 拓扑：parallel
- 执行方式：real-subagent
- 真实派发：yes
- 能力召回：family:sxlb-governance
- delegation 可用性：available
- 本线办理理由：not-needed
- 派发就绪状态：ready-for-agent
- 返回审议点：门下复核
- 合流要求：merge required
- 合流摘要：subagents/merge-summary.md
- 执行预算：completion review plus one readiness dashboard
- 修复循环上限：two evidence-fix loops before recall
- 预算超限处理：return to 尚书省

## 官署分派

- 官署：工部
- 分支编号：office-01
- 任务：Implement scripts
- 切片类型：support slice
- 交互模式：AFK
- blocked-by：none
- 验收标准：branch return includes verification evidence and touched files
- 所有权：scripts/
- 共享只读：tests/
- 禁写范围：protocols/
- 可写范围：scripts/, tests/
- 危险命令策略：no destructive commands
- 需额外批准动作：none
- 整合者：工部
- 允许技能：python
- 禁止越权：do not edit protocols
- 分支执行：real-subagent
- 工作包：subagents/subagent-work-packet-office-01.md
- 回传物：subagents/returns/subagent-return-office-01.md
- 升级条件：boundary conflict

- 官署：刑部
- 分支编号：office-02
- 任务：Verify scripts
- 切片类型：verification slice
- 交互模式：AFK
- blocked-by：none
- 验收标准：tests pass and verification evidence is recorded
- 所有权：tests/
- 共享只读：scripts/
- 禁写范围：protocols/
- 可写范围：scripts/, tests/
- 危险命令策略：no destructive commands
- 需额外批准动作：none
- 整合者：工部
- 允许技能：python, unittest
- 禁止越权：do not edit protocols
- 分支执行：real-subagent
- 工作包：subagents/subagent-work-packet-office-02.md
- 回传物：subagents/returns/subagent-return-office-02.md
- 升级条件：verification ambiguity

## 双轨附记

- 文线：n/a
- 武线：工部与刑部并行
- 合流点：门下复核
- 合流负责：工部
""",
    )
    write(
        root / "artifact-registry.md",
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
    )
    write(
        root / "records-routing.md",
        """# 记录分流

## 分流决策

- canonical：none
- report-only：minor implementation notes
- restart-update：none
- no-writeback：none
""",
    )
    write(
        root / "verification.md",
        """# 验证矩阵

## 验证概览

- 验证目标：completion package
- 受影响对象：sxlb case package
- 验证结论：pass
- 行为断言/不变量：completion package remains reviewable and guard-valid
- 测试有效性：guard validation fails when required evidence fields are missing

## 验证证据

- 命令或动作：python -m unittest
- 结果：pass
- 失败项：none
- 复验：pass
- 未覆盖风险：minor residual integration risk
""",
    )
    write(
        root / "memorial-report.md",
        f"""# 回奏

## 任务总结

- 任务：Review a governed case
- 使用链路：太子 -> 中书省 -> 门下省 -> 尚书省 -> 六部 -> 门下复核 -> 回奏
- 当前结果：completed
- 停止原因：n/a
- 停止时状态：门下复核
- 门下复核依据：menxia-review.md

## 核心决策

- 关键决策：Require real review evidence before memorialization
- 双轨合流：subagents/merge-summary.md

## 验证与风险

- 验证证据：{verification_evidence}
- 未完成/未验证项：none
- 剩余风险：minor residual integration risk

## 记录分流

- 案卷归档：/tmp/example
- 项目复盘：/tmp/example/retrospective.md
- canonical 更新：none
- restart 更新：none

## 复盘四问

- 顺的地方：Artifacts stayed bounded
- 卡的地方：none
- 返工点：none
- 下次项目内应改进之处：automate more review prep

## 下一步建议

- 推荐动作：allow memorialization if review passes
- 是否继续在 sxlb 中：yes
""",
    )
    write(
        root / "subagents" / "subagent-work-packet-office-01.md",
        """# 子代理工作包

## 工作包信息

- 案件编号：demo-case
- 分支编号：office-01
- 所属官署：工部
- 执行方式：real-subagent
- 派发来源：dispatch-order.md
- 返回物：subagent-return-office-01.md
""",
    )
    write(
        root / "subagents" / "subagent-work-packet-office-02.md",
        """# 子代理工作包

## 工作包信息

- 案件编号：demo-case
- 分支编号：office-02
- 所属官署：刑部
- 执行方式：real-subagent
- 派发来源：dispatch-order.md
- 返回物：subagent-return-office-02.md
""",
    )
    write(
        root / "subagents" / "returns" / "subagent-return-office-01.md",
        """# 子代理回传物

## 基本信息

- 案件编号：demo-case
- 分支编号：office-01
- 所属官署：工部
- 工作包引用：subagent-work-packet-office-01.md
- 回传状态：complete

## 结果摘要

- 已完成内容：implemented the script branch
- 未完成内容：none
- 关键判断：ready for merge

## 证据与产物

- 触达文件/产物：scripts/subagent_dispatch.py
- 新增证据：unit tests passed for script branch
- 关键命令或动作：python -m unittest ...

## 边界声明

- 是否越权：no
- 边界异常：none
- 需要召回或调整派发：no

## 合流输入

- 对其他分支的依赖：office-02 verification
- 已知冲突：none
- 建议下一步：merge
- 剩余风险：none
""",
    )
    write(
        root / "subagents" / "returns" / "subagent-return-office-02.md",
        """# 子代理回传物

## 基本信息

- 案件编号：demo-case
- 分支编号：office-02
- 所属官署：刑部
- 工作包引用：subagent-work-packet-office-02.md
- 回传状态：complete

## 结果摘要

- 已完成内容：verified the script branch
- 未完成内容：none
- 关键判断：ready for merge

## 证据与产物

- 触达文件/产物：tests/test_subagent_dispatch.py
- 新增证据：verification review passed
- 关键命令或动作：python -m unittest ...

## 边界声明

- 是否越权：no
- 边界异常：none
- 需要召回或调整派发：no

## 合流输入

- 对其他分支的依赖：office-01 implementation
- 已知冲突：none
- 建议下一步：merge
- 剩余风险：none
""",
    )
    write(
        root / "subagents" / "merge-summary.md",
        """# 合流摘要

## 合流信息

- 案件编号：demo-case
- 合流负责人：工部
- 合流阶段：门下复核
- 参与分支：office-01, office-02
- 输入回传物：subagents/returns/subagent-return-office-01.md, subagents/returns/subagent-return-office-02.md

## 分支汇总

- 分支编号：office-01
- 官署：工部
- 回传状态：complete
- 可纳入成果：implementation branch accepted
- 暂不采纳部分：none

- 分支编号：office-02
- 官署：刑部
- 回传状态：complete
- 可纳入成果：verification branch accepted
- 暂不采纳部分：none

## 冲突与处理

- 分支冲突：none
- 处理方式：resolved
- 仍待裁决：none

## 门下复核输入

- 合流后的主张：all required execution and verification artifacts are present
- 依据材料：dispatch-order.md plus branch returns
- 剩余风险：minor residual integration risk
- 请求结论：allow review
""",
    )
    write(
        root / "learning-candidates.jsonl",
        '{"type":"governance","scope":"project","source":"retrospective","confidence":6,"summary":"Keep governed completion review explicit","promote_to":"none","stale_when":"menxia review protocol changes"}\n',
    )
    write(
        root / "event-ledger.md",
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
  摘要：Parallel order issued
  证据：dispatch-order.md, shangshu-dispatch-summary.md

- 时间：2026-04-23T10:20:00
  状态：待回奏
  动作：memorial
  发起：礼部
  摘要：Memorial draft prepared
  证据：memorial-report.md
""",
    )
    write(
        root / "zhongshu-plan.md",
        """# 中书方案

## 目标与边界

- 目标：Review a governed case
- 不做什么：Do not skip review
- 成功标准：Only complete cases pass

## 任务拆解

- 主任务：review completion package
- 子任务：inspect return and merge evidence
- 风险与未知：none

## 预算与停止条件

- 工具/轮次预算：one completion review run
- 修复循环上限：two evidence-fix loops before recall
- 停止/升级条件：return to 尚书省 if evidence remains incomplete

## 双轨规划

- 文线：n/a
- 武线：n/a
- 合流规则：n/a

## 路由建议

- 任务类别：C
- 推荐链路：太子 -> 中书省 -> 门下省 -> 尚书省 -> 六部 -> 门下复核 -> 回奏
- 需要审议的问题：is the evidence sufficient

## 技能与官署映射

- 主要官署：门下省, 刑部
- 主要技能：superpowers:verification-before-completion
- 额外技能：none
- 能力召回：family:sxlb-governance
""",
    )


class MenxiaReviewTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="sxlb-menxia-"))

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir)

    def test_passes_complete_case_and_writes_review(self) -> None:
        make_review_case(self.temp_dir)
        result = run_completion_review(self.temp_dir, force=True)
        self.assertEqual(result["verdict"], "通过")
        self.assertTrue(result["allow_memorial"])
        review_text = (self.temp_dir / "menxia-review.md").read_text(encoding="utf-8")
        self.assertIn("是否准许回奏：yes", review_text)
        self.assertIn("结论：通过", review_text)
        self.assertIn("审批台账输入：n/a", review_text)
        self.assertIn("审批台账检查：n/a", review_text)
        self.assertIn("四问-假设检查：manual", review_text)
        self.assertIn("PRD/领域语言检查：manual", review_text)
        self.assertIn("预算与停止条件检查：manual", review_text)
        self.assertIn("冲突取舍检查：manual", review_text)
        self.assertIn("失败显性化检查：pass", review_text)
        self.assertIn("HITL/AFK 检查：pass", review_text)
        self.assertIn("blocked-by/ready-for-agent 检查：pass", review_text)
        ledger_text = (self.temp_dir / "event-ledger.md").read_text(encoding="utf-8")
        self.assertIn("动作：review", ledger_text)
        self.assertIn("证据：menxia-review.md", ledger_text)

    def test_blocks_when_merge_artifact_missing(self) -> None:
        make_review_case(self.temp_dir)
        (self.temp_dir / "subagents" / "merge-summary.md").unlink()
        result = run_completion_review(self.temp_dir, force=True)
        self.assertEqual(result["verdict"], "补证后再审")
        self.assertFalse(result["allow_memorial"])
        self.assertTrue(any("merge summary" in issue.lower() or "merge" in issue.lower() for issue in result["issues"]))

    def test_blocks_when_verification_evidence_is_missing(self) -> None:
        make_review_case(self.temp_dir, verification_evidence="none")
        result = run_completion_review(self.temp_dir, force=True)
        self.assertEqual(result["verdict"], "补证后再审")
        self.assertFalse(result["allow_memorial"])
        self.assertTrue(any("verification" in issue.lower() for issue in result["issues"]))

    def test_writes_readiness_dashboard(self) -> None:
        make_review_case(self.temp_dir)
        result = run_completion_review(self.temp_dir, force=True)
        self.assertEqual(result["verdict"], "通过")
        readiness_path = self.temp_dir / "menxia-readiness.md"
        self.assertTrue(readiness_path.exists())
        readiness_text = readiness_path.read_text(encoding="utf-8")
        self.assertIn("| Gate | Required | Status | Evidence |", readiness_text)
        self.assertIn("| 验证证据 | yes | pass | verification.md |", readiness_text)
        self.assertIn("| 测试有效性 | yes | pass | verification.md |", readiness_text)

    def test_generates_approval_ledger_during_completion_review(self) -> None:
        make_review_case(self.temp_dir)
        dispatch_path = self.temp_dir / "dispatch-order.md"
        dispatch_path.write_text(
            dispatch_path.read_text(encoding="utf-8")
            .replace("- 危险命令策略：no destructive commands", "- 危险命令策略：approval required")
            .replace("- 需额外批准动作：none", "- 需额外批准动作：destructive commands"),
            encoding="utf-8",
        )
        return_path = self.temp_dir / "subagents" / "returns" / "subagent-return-office-01.md"
        return_path.write_text(
            return_path.read_text(encoding="utf-8").replace(
                "- 关键命令或动作：python -m unittest ...",
                "- 关键命令或动作：git reset --hard HEAD~1\n- 额外批准证据：user approved destructive reset in current thread",
            ),
            encoding="utf-8",
        )
        memorial_path = self.temp_dir / "memorial-report.md"
        memorial_path.write_text(
            memorial_path.read_text(encoding="utf-8").replace("- canonical 更新：none", "- canonical 更新：/tmp/canonical.md"),
            encoding="utf-8",
        )
        result = run_completion_review(self.temp_dir, force=True)
        self.assertEqual(result["verdict"], "通过")
        approval_ledger = (self.temp_dir / "approval-ledger.md").read_text(encoding="utf-8")
        self.assertIn("| office-01 |", approval_ledger)
        self.assertIn("| present |", approval_ledger)
        objection_review = (self.temp_dir / "objection-review.md").read_text(encoding="utf-8")
        self.assertIn("是否阻断：no", objection_review)
        review_text = (self.temp_dir / "menxia-review.md").read_text(encoding="utf-8")
        self.assertIn("审批台账输入：approval-ledger.md", review_text)
        self.assertIn("审批台账检查：pass", review_text)
        readiness_text = (self.temp_dir / "menxia-readiness.md").read_text(encoding="utf-8")
        self.assertIn("| 审批台账 | conditional | pass | approval-ledger.md |", readiness_text)

    def test_readiness_marks_approval_gate_na_without_dangerous_commands(self) -> None:
        make_review_case(self.temp_dir)
        result = run_completion_review(self.temp_dir, force=True)
        self.assertEqual(result["verdict"], "通过")
        readiness_text = (self.temp_dir / "menxia-readiness.md").read_text(encoding="utf-8")
        self.assertIn("| 审批台账 | conditional | n/a | n/a |", readiness_text)


if __name__ == "__main__":
    unittest.main()

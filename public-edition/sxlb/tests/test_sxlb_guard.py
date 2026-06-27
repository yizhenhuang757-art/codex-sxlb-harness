import shutil
import tempfile
import unittest
from pathlib import Path

from sxlb_guard import validate_case_dir


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def make_valid_case_package(root: Path) -> None:
    write(
        root / "case.md",
        """# 立案单

## 基本信息

- 任务：Build hard framework
- 用户目标：Make sxlb enforceable
- 约束：Keep it text-first
- 风险级别：medium
- 案卷路径：$SXLB_CASE_ROOT/sxlb/example
- restart 目标：n/a
- 能力召回：family:sxlb-governance, family:automation-integration

## 任务分类

- 任务类别：C
- 最小合法链路：太子 -> 尚书省 -> 单部执行 -> 门下复核 -> 回奏
- 当前建议链路：太子 -> 中书省 -> 门下省 -> 尚书省 -> 六部 -> 门下复核 -> 回奏
- 首办官署：中书省
- 下一站：中书省

## 立案备注

- 关键未知：none
- 需要用户确认：no
- 可能更新的 canonical：/tmp/canonical.md
""",
    )
    write(
        root / "zhongshu-plan.md",
        """# 中书方案

## 目标与边界

- 目标：Build hard framework
- 不做什么：No hidden daemon
- 成功标准：Validator and scaffolder work

## 任务拆解

- 主任务：Implement scripts
- 子任务：Add templates and tests
- 风险与未知：None

## 预算与停止条件

- 工具/轮次预算：targeted unit-test pass plus one guard review
- 修复循环上限：two corrective loops before 门下复核
- 停止/升级条件：return to 门下省 if guard errors remain ambiguous

## 双轨规划

- 文线：Protocol updates
- 武线：Script implementation
- 合流规则：Merge before completion review

## 路由建议

- 任务类别：C
- 推荐链路：太子 -> 中书省 -> 门下省 -> 尚书省 -> 六部 -> 门下复核 -> 回奏
- 需要审议的问题：Are the checks sufficient

## 技能与官署映射

- 主要官署：工部, 吏部, 礼部
- 主要技能：planning-with-files
- 额外技能：superpowers:verification-before-completion
- 能力召回：family:sxlb-governance, family:automation-integration
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
- 能力召回：family:sxlb-governance, family:automation-integration
- delegation 可用性：available
- 本线办理理由：not-needed
- 派发就绪状态：ready-for-agent
- 返回审议点：门下复核
- 合流要求：merge required
- 合流摘要：subagents/merge-summary.md
- 执行预算：targeted unit tests plus guard validation
- 修复循环上限：two fix loops before recall
- 预算超限处理：return to 尚书省

## 官署分派

- 官署：工部
- 分支编号：office-01
- 任务：Build scripts
- 切片类型：support slice
- 交互模式：AFK
- blocked-by：none
- 验收标准：scripts and tests pass with explicit return evidence
- 所有权：scripts/
- 共享只读：protocol docs
- 禁写范围：canonical docs
- 可写范围：scripts/, tests/
- 真实触达审计：not required
- 危险命令策略：no destructive commands
- 需额外批准动作：none
- 整合者：工部
- 允许技能：python
- 禁止越权：do not change canonical claims
- 分支执行：real-subagent
- 工作包：subagents/subagent-work-packet-office-01.md
- 回传物：subagents/returns/subagent-return-office-01.md
- 升级条件：boundary conflict or missing evidence

## 双轨附记

- 文线：礼部更新协议
- 武线：工部写脚本
- 合流点：门下复核
- 合流负责：工部
""",
    )
    write(
        root / "menxia-review.md",
        """# 门下复核单

## 审议对象

- 来源：completion claim
- 审议类型：completion
- 当前阶段：门下复核
- 审议范围：full package
- 派令引用：dispatch-order.md
- 工作包输入：subagents/subagent-work-packet-office-01.md
- 回传输入：subagents/returns/subagent-return-office-01.md
- 合流输入：subagents/merge-summary.md

## 审议结论

- 结论：通过
- 主要依据：tests passed and package complete

## 发现

- 合法链路检查：pass
- 官署归属检查：pass
- 真实派发检查：required and satisfied
- 预算与停止条件检查：pass
- 冲突取舍检查：pass
- 工作包边界检查：pass
- 回传完备检查：pass
- 合流依据检查：pass
- 范围问题：none
- 分支冲突问题：none
- 验证问题：none
- 失败显性化检查：pass
- 技能匹配问题：none
- 路由问题：none

## 下一步

- 返回状态：待回奏
- 返回官署：礼部
- 是否准许回奏：yes
- 补充要求：none
""",
    )
    write(
        root / "memorial-report.md",
        """# 回奏

## 任务总结

- 任务：Build hard framework
- 使用链路：太子 -> 中书省 -> 门下省 -> 尚书省 -> 六部 -> 门下复核 -> 回奏
- 当前结果：completed
- 停止原因：n/a
- 停止时状态：待分流
- 门下复核依据：menxia-review passed

## 核心决策

- 关键决策：Use scripts plus templates
- 双轨合流：Merged before completion review

## 验证与风险

- 验证证据：unit tests passed
- 未完成/未验证项：none
- 剩余风险：manual discipline still matters

## 记录分流

- 案卷归档：/tmp/example
- 项目复盘：/tmp/example/retrospective.md
- canonical 更新：/tmp/canonical.md
- restart 更新：/tmp/restart.md

## 复盘四问

- 顺的地方：Validator shape became clear
- 卡的地方：Sandbox write restriction
- 返工点：Legacy terminology cleanup
- 下次项目内应改进之处：Add transcript-aware adapters

## 下一步建议

- 推荐动作：Run on a live case
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
        root / "subagents" / "returns" / "subagent-return-office-01.md",
        """# 子代理回传物

## 基本信息

- 案件编号：demo-case
- 分支编号：office-01
- 所属官署：工部
- 工作包引用：subagent-work-packet-office-01.md
- 回传状态：complete
- 触达文件/产物：scripts/subagent_dispatch.py
""",
    )
    write(
        root / "subagents" / "merge-summary.md",
        """# 合流摘要

## 合流信息

- 案件编号：demo-case
- 合流负责人：工部
- 合流阶段：门下复核
- 参与分支：office-01
- 输入回传物：subagents/returns/subagent-return-office-01.md
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

- canonical：/tmp/canonical.md
- report-only：none
- restart-update：/tmp/restart.md
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
- 行为断言/不变量：completion package remains guard-valid
- 测试有效性：unit test can fail when required guard fields are missing

## 验证证据

- 命令或动作：python -m unittest
- 结果：pass
- 失败项：none
- 复验：pass
- 未覆盖风险：minor residual integration risk
""",
    )
    write(
        root / "menxia-readiness.md",
        """# 门下 readiness dashboard

| Gate | Required | Status | Evidence |
|---|---:|---|---|
| 中书方案 | yes | pass | zhongshu-plan.md |
| 派令 | yes | pass | dispatch-order.md |
| 验证证据 | yes | pass | verification.md |
""",
    )
    write(
        root / "learning-candidates.jsonl",
        '{"type":"governance","scope":"project","source":"retrospective","confidence":6,"summary":"Keep case learning separate from canonical promotion","promote_to":"none","stale_when":"sxlb closure protocol changes"}\n',
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
  证据：dispatch-order.md

- 时间：2026-04-23T10:20:00
  状态：待回奏
  动作：memorial
  发起：礼部
  摘要：Memorial drafted
  证据：memorial-report.md
""",
    )


class SXLBGuardTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="sxlb-guard-"))

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir)

    def test_accepts_well_formed_completion_package(self) -> None:
        make_valid_case_package(self.temp_dir)
        result = validate_case_dir(self.temp_dir, phase="completion")
        self.assertTrue(result.ok, result.errors)

    def test_completion_blocks_missing_capability_recall_field(self) -> None:
        make_valid_case_package(self.temp_dir)
        case_path = self.temp_dir / "case.md"
        case_path.write_text(
            case_path.read_text(encoding="utf-8").replace("- 能力召回：family:sxlb-governance, family:automation-integration\n", ""),
            encoding="utf-8",
        )

        result = validate_case_dir(self.temp_dir, phase="completion")

        self.assertFalse(result.ok)
        self.assertIn("case.md is missing field: 能力召回", result.errors)

    def test_requires_zhongshu_plan_when_event_ledger_reaches_zhongshu(self) -> None:
        make_valid_case_package(self.temp_dir)
        case_path = self.temp_dir / "case.md"
        case_path.write_text(case_path.read_text(encoding="utf-8").replace("- 任务类别：C", "- 任务类别：A"), encoding="utf-8")
        (self.temp_dir / "zhongshu-plan.md").unlink()
        result = validate_case_dir(self.temp_dir, phase="completion")
        self.assertFalse(result.ok)
        self.assertIn("event-ledger.md state 中书拟制 requires zhongshu-plan.md", result.errors)

    def test_requires_dispatch_order_when_event_ledger_reaches_shangshu(self) -> None:
        make_valid_case_package(self.temp_dir)
        (self.temp_dir / "dispatch-order.md").unlink()
        result = validate_case_dir(self.temp_dir, phase="completion")
        self.assertFalse(result.ok)
        self.assertIn("event-ledger.md state 尚书派发 requires dispatch-order.md", result.errors)

    def test_requires_external_evidence_when_caifeng_reaches_package_state(self) -> None:
        make_valid_case_package(self.temp_dir)
        ledger_path = self.temp_dir / "event-ledger.md"
        ledger_path.write_text(
            ledger_path.read_text(encoding="utf-8")
            + "\n- 时间：2026-04-23T10:06:00\n  状态：中书拟制\n  采风：已入方案\n  动作：plan\n  发起：中书省\n  摘要：Evidence entered the plan\n  证据：none\n",
            encoding="utf-8",
        )
        result = validate_case_dir(self.temp_dir, phase="completion")
        self.assertFalse(result.ok)
        self.assertIn(
            "event-ledger.md caifeng state 已入方案 requires zhongshu-plan.md evidence reference or an external evidence package",
            result.errors,
        )

    def test_accepts_caifeng_package_state_with_external_evidence_artifact(self) -> None:
        make_valid_case_package(self.temp_dir)
        ledger_path = self.temp_dir / "event-ledger.md"
        ledger_path.write_text(
            ledger_path.read_text(encoding="utf-8")
            + "\n- 时间：2026-04-23T10:06:00\n  状态：中书拟制\n  采风：证据包待审\n  动作：plan\n  发起：中书省\n  摘要：Evidence package ready\n  证据：external-evidence.md\n",
            encoding="utf-8",
        )
        write(
            self.temp_dir / "external-evidence.md",
            "# 外部证据包\n\n- 调研问题：guard consistency\n- 来源清单：local fixture\n- 来源类型：official\n- 检查日期：2026-05-06\n- 来源可靠性：primary local fixture\n- 可用结论：guard consistency is supported\n- 不确定性：none\n- 决策影响：supports plan\n",
        )
        result = validate_case_dir(self.temp_dir, phase="completion")
        self.assertTrue(result.ok, result.errors)

    def test_rejects_caifeng_evidence_package_without_source_reliability(self) -> None:
        make_valid_case_package(self.temp_dir)
        ledger_path = self.temp_dir / "event-ledger.md"
        ledger_path.write_text(
            ledger_path.read_text(encoding="utf-8")
            + "\n- 时间：2026-04-23T10:06:00\n  状态：中书拟制\n  采风：证据包待审\n  动作：plan\n  发起：中书省\n  摘要：Evidence package ready\n  证据：external-evidence.md\n",
            encoding="utf-8",
        )
        write(
            self.temp_dir / "external-evidence.md",
            "# 外部证据包\n\n- 调研问题：guard consistency\n- 来源清单：local fixture\n- 决策影响：supports plan\n",
        )
        result = validate_case_dir(self.temp_dir, phase="completion")
        self.assertFalse(result.ok)
        self.assertIn("external-evidence.md is missing external evidence field: 来源可靠性", result.errors)

    def test_rejects_caifeng_evidence_package_with_invalid_source_type(self) -> None:
        make_valid_case_package(self.temp_dir)
        ledger_path = self.temp_dir / "event-ledger.md"
        ledger_path.write_text(
            ledger_path.read_text(encoding="utf-8")
            + "\n- 时间：2026-04-23T10:06:00\n  状态：中书拟制\n  采风：已入方案\n  动作：plan\n  发起：中书省\n  摘要：Evidence entered the plan\n  证据：external-evidence.md\n",
            encoding="utf-8",
        )
        write(
            self.temp_dir / "external-evidence.md",
            "# 外部证据包\n\n- 调研问题：guard consistency\n- 来源清单：local fixture\n- 来源类型：rumor\n- 检查日期：2026-05-06\n- 来源可靠性：weak\n- 可用结论：maybe\n- 不确定性：high\n- 决策影响：none\n",
        )
        result = validate_case_dir(self.temp_dir, phase="completion")
        self.assertFalse(result.ok)
        self.assertTrue(any("invalid 来源类型" in error for error in result.errors))

    def test_rejects_invalid_execution_observations_jsonl(self) -> None:
        make_valid_case_package(self.temp_dir)
        write(self.temp_dir / "execution-observations.jsonl", "{bad json}\n")
        result = validate_case_dir(self.temp_dir, phase="completion")
        self.assertFalse(result.ok)
        self.assertTrue(any("execution-observations.jsonl line 1 is not valid JSON" in error for error in result.errors))

    def test_rejects_execution_observation_without_promotion_boundary(self) -> None:
        make_valid_case_package(self.temp_dir)
        write(
            self.temp_dir / "execution-observations.jsonl",
            '{"time":"2026-05-06T10:00:00Z","office":"工部","source":"test","event":"runtime-friction","evidence":{"detail":"x"},"candidate":"promote me","confidence":"medium"}\n',
        )
        result = validate_case_dir(self.temp_dir, phase="completion")
        self.assertFalse(result.ok)
        self.assertIn("execution observation line 1 is missing field: promote_to", result.errors)

    def test_rejects_execution_observation_direct_canonical_promotion(self) -> None:
        make_valid_case_package(self.temp_dir)
        write(
            self.temp_dir / "execution-observations.jsonl",
            '{"time":"2026-05-06T10:00:00Z","office":"工部","source":"test","event":"runtime-friction","evidence":{"detail":"x"},"candidate":"promote me","promote_to":"canonical","confidence":"medium"}\n',
        )
        result = validate_case_dir(self.temp_dir, phase="completion")
        self.assertFalse(result.ok)
        self.assertIn("execution observation line 1 has invalid promote_to: canonical", result.errors)

    def test_accepts_structured_execution_observations_jsonl(self) -> None:
        make_valid_case_package(self.temp_dir)
        write(
            self.temp_dir / "execution-observations.jsonl",
            '{"time":"2026-05-06T10:00:00Z","office":"工部","source":"test","event":"runtime-friction","evidence":{"detail":"x"},"candidate":"review later","promote_to":"learning-candidates.jsonl","confidence":"medium"}\n',
        )
        result = validate_case_dir(self.temp_dir, phase="completion")
        self.assertTrue(result.ok, result.errors)

    def test_rejects_legacy_direct_handling_chain(self) -> None:
        make_valid_case_package(self.temp_dir)
        case_path = self.temp_dir / "case.md"
        case_path.write_text(case_path.read_text(encoding="utf-8").replace("门下复核 -> 回奏", "direct handling -> 回奏"), encoding="utf-8")
        result = validate_case_dir(self.temp_dir, phase="completion")
        self.assertFalse(result.ok)
        self.assertTrue(any("forbidden legacy route token" in error for error in result.errors))

    def test_rejects_missing_required_file(self) -> None:
        make_valid_case_package(self.temp_dir)
        (self.temp_dir / "dispatch-order.md").unlink()
        result = validate_case_dir(self.temp_dir, phase="completion")
        self.assertFalse(result.ok)
        self.assertIn("Missing required file: dispatch-order.md", result.errors)

    def test_rejects_missing_real_subagent_artifacts(self) -> None:
        make_valid_case_package(self.temp_dir)
        (self.temp_dir / "subagents" / "returns" / "subagent-return-office-01.md").unlink()
        result = validate_case_dir(self.temp_dir, phase="completion")
        self.assertFalse(result.ok)
        self.assertIn(
            "Referenced subagent return is missing: subagents/returns/subagent-return-office-01.md",
            result.errors,
        )

    def test_requires_learning_candidates_for_bcd_completion(self) -> None:
        make_valid_case_package(self.temp_dir)
        (self.temp_dir / "learning-candidates.jsonl").unlink()
        result = validate_case_dir(self.temp_dir, phase="completion")
        self.assertFalse(result.ok)
        self.assertIn("Missing required file: learning-candidates.jsonl", result.errors)

    def test_rejects_empty_learning_candidates_for_bcd_completion(self) -> None:
        make_valid_case_package(self.temp_dir)
        (self.temp_dir / "learning-candidates.jsonl").write_text("", encoding="utf-8")
        result = validate_case_dir(self.temp_dir, phase="completion")
        self.assertFalse(result.ok)
        self.assertIn(
            "learning-candidates.jsonl must contain a learning candidate or an explicit no-learning record at completion",
            result.errors,
        )

    def test_accepts_explicit_no_learning_record_for_bcd_completion(self) -> None:
        make_valid_case_package(self.temp_dir)
        (self.temp_dir / "learning-candidates.jsonl").write_text(
            '{"type":"no-learning","scope":"case","source":"menxia-review","confidence":6,"summary":"No reusable project or agent learning justified for this case","promote_to":"none","stale_when":"new evidence appears"}\n',
            encoding="utf-8",
        )
        result = validate_case_dir(self.temp_dir, phase="completion")
        self.assertTrue(result.ok, result.errors)

    def test_rejects_invalid_learning_candidate_jsonl(self) -> None:
        make_valid_case_package(self.temp_dir)
        (self.temp_dir / "learning-candidates.jsonl").write_text("{bad json}\n", encoding="utf-8")
        result = validate_case_dir(self.temp_dir, phase="completion")
        self.assertFalse(result.ok)
        self.assertTrue(any("learning-candidates.jsonl line 1 is not valid JSON" in error for error in result.errors))

    def test_rejects_learning_candidate_without_promotion_gate(self) -> None:
        make_valid_case_package(self.temp_dir)
        (self.temp_dir / "learning-candidates.jsonl").write_text(
            '{"type":"governance","scope":"project","source":"retrospective","confidence":6,"summary":"Missing gate"}\n',
            encoding="utf-8",
        )
        result = validate_case_dir(self.temp_dir, phase="completion")
        self.assertFalse(result.ok)
        self.assertTrue(any("learning candidate line 1 is missing field: promote_to" in error for error in result.errors))

    def test_requires_artifact_registry_for_bcd_completion(self) -> None:
        make_valid_case_package(self.temp_dir)
        (self.temp_dir / "artifact-registry.md").unlink()
        result = validate_case_dir(self.temp_dir, phase="completion")
        self.assertFalse(result.ok)
        self.assertIn("Missing required file: artifact-registry.md", result.errors)

    def test_requires_verification_matrix_for_bcd_completion(self) -> None:
        make_valid_case_package(self.temp_dir)
        (self.temp_dir / "verification.md").unlink()
        result = validate_case_dir(self.temp_dir, phase="completion")
        self.assertFalse(result.ok)
        self.assertIn("Missing required file: verification.md", result.errors)

    def test_requires_dispatch_write_scope_fields(self) -> None:
        make_valid_case_package(self.temp_dir)
        path = self.temp_dir / "dispatch-order.md"
        path.write_text(path.read_text(encoding="utf-8").replace("- 可写范围：scripts/, tests/\n", ""), encoding="utf-8")
        result = validate_case_dir(self.temp_dir, phase="completion")
        self.assertFalse(result.ok)
        self.assertTrue(any("missing 可写范围" in error for error in result.errors))

    def test_rejects_verification_without_result(self) -> None:
        make_valid_case_package(self.temp_dir)
        path = self.temp_dir / "verification.md"
        path.write_text(path.read_text(encoding="utf-8").replace("- 结果：pass", "- 结果：none"), encoding="utf-8")
        result = validate_case_dir(self.temp_dir, phase="completion")
        self.assertFalse(result.ok)
        self.assertTrue(any("verification.md" in error and "结果" in error for error in result.errors))

    def test_requires_agent_failure_control_fields_at_completion(self) -> None:
        make_valid_case_package(self.temp_dir)
        verification_path = self.temp_dir / "verification.md"
        verification_path.write_text(
            verification_path.read_text(encoding="utf-8")
            .replace("- 行为断言/不变量：completion package remains guard-valid\n", "")
            .replace("- 测试有效性：unit test can fail when required guard fields are missing\n", ""),
            encoding="utf-8",
        )
        memorial_path = self.temp_dir / "memorial-report.md"
        memorial_path.write_text(
            memorial_path.read_text(encoding="utf-8").replace("- 未完成/未验证项：none\n", ""),
            encoding="utf-8",
        )

        result = validate_case_dir(self.temp_dir, phase="completion")

        self.assertFalse(result.ok)
        self.assertIn("verification.md is missing field: 行为断言/不变量", result.errors)
        self.assertIn("verification.md is missing field: 测试有效性", result.errors)
        self.assertIn("memorial-report.md is missing field: 未完成/未验证项", result.errors)

    def test_rejects_temporary_case_archive_at_completion(self) -> None:
        make_valid_case_package(self.temp_dir)
        case_path = self.temp_dir / "case.md"
        case_path.write_text(
            case_path.read_text(encoding="utf-8").replace(
                "- 案卷路径：$SXLB_CASE_ROOT/sxlb/example",
                "- 案卷路径：/private/tmp/sxlb-fragment-calendar-nav",
            ),
            encoding="utf-8",
        )
        result = validate_case_dir(self.temp_dir, phase="completion")
        self.assertFalse(result.ok)
        self.assertIn("case.md 案卷路径 cannot remain in a temporary directory at completion", result.errors)

    def test_rejects_real_subagent_return_touching_forbidden_scope(self) -> None:
        make_valid_case_package(self.temp_dir)
        return_path = self.temp_dir / "subagents" / "returns" / "subagent-return-office-01.md"
        return_path.write_text(
            return_path.read_text(encoding="utf-8").replace(
                "- 触达文件/产物：scripts/subagent_dispatch.py",
                "- 触达文件/产物：canonical/rules.md",
            ),
            encoding="utf-8",
        )
        dispatch_path = self.temp_dir / "dispatch-order.md"
        dispatch_path.write_text(
            dispatch_path.read_text(encoding="utf-8").replace(
                "- 禁写范围：canonical docs",
                "- 禁写范围：canonical/",
            ),
            encoding="utf-8",
        )
        result = validate_case_dir(self.temp_dir, phase="completion")
        self.assertFalse(result.ok)
        self.assertTrue(any("touches forbidden scope" in error for error in result.errors))

    def test_rejects_real_subagent_return_outside_writable_scope(self) -> None:
        make_valid_case_package(self.temp_dir)
        return_path = self.temp_dir / "subagents" / "returns" / "subagent-return-office-01.md"
        return_path.write_text(
            return_path.read_text(encoding="utf-8").replace(
                "- 触达文件/产物：scripts/subagent_dispatch.py",
                "- 触达文件/产物：docs/notes.md",
            ),
            encoding="utf-8",
        )
        result = validate_case_dir(self.temp_dir, phase="completion")
        self.assertFalse(result.ok)
        self.assertTrue(any("outside writable scope" in error for error in result.errors))

    def test_requires_actual_touched_file_when_audit_is_required(self) -> None:
        make_valid_case_package(self.temp_dir)
        dispatch_path = self.temp_dir / "dispatch-order.md"
        dispatch_path.write_text(
            dispatch_path.read_text(encoding="utf-8").replace(
                "- 真实触达审计：not required",
                "- 真实触达审计：required",
            ),
            encoding="utf-8",
        )
        result = validate_case_dir(self.temp_dir, phase="completion")
        self.assertFalse(result.ok)
        self.assertTrue(any("requires actual touched-files evidence" in error for error in result.errors))

    def test_actual_touched_file_overrides_return_self_report_for_scope_audit(self) -> None:
        make_valid_case_package(self.temp_dir)
        dispatch_path = self.temp_dir / "dispatch-order.md"
        dispatch_path.write_text(
            dispatch_path.read_text(encoding="utf-8").replace(
                "- 真实触达审计：not required",
                "- 真实触达审计：required",
            ),
            encoding="utf-8",
        )
        return_path = self.temp_dir / "subagents" / "returns" / "subagent-return-office-01.md"
        return_path.write_text(
            return_path.read_text(encoding="utf-8").replace(
                "- 触达文件/产物：scripts/subagent_dispatch.py",
                "- 触达文件/产物：scripts/subagent_dispatch.py\n- 真实触达清单：subagents/returns/touched-files-office-01.txt",
            ),
            encoding="utf-8",
        )
        write(
            self.temp_dir / "subagents" / "returns" / "touched-files-office-01.txt",
            "# generated by git diff --name-only\n\ndocs/notes.md\n",
        )
        result = validate_case_dir(self.temp_dir, phase="completion")
        self.assertFalse(result.ok)
        self.assertTrue(any("outside writable scope" in error and "docs/notes.md" in error for error in result.errors))

    def test_rejects_destructive_command_when_policy_forbids_it(self) -> None:
        make_valid_case_package(self.temp_dir)
        return_path = self.temp_dir / "subagents" / "returns" / "subagent-return-office-01.md"
        return_path.write_text(
            return_path.read_text(encoding="utf-8").replace(
                "- 回传状态：complete",
                "- 回传状态：complete\n- 关键命令或动作：rm -rf scripts/cache",
            ),
            encoding="utf-8",
        )
        result = validate_case_dir(self.temp_dir, phase="completion")
        self.assertFalse(result.ok)
        self.assertTrue(any("destructive command forbidden" in error for error in result.errors))

    def test_requires_extra_approval_evidence_for_approval_gated_dangerous_command(self) -> None:
        make_valid_case_package(self.temp_dir)
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
                "- 回传状态：complete",
                "- 回传状态：complete\n- 关键命令或动作：git reset --hard HEAD~1",
            ),
            encoding="utf-8",
        )
        result = validate_case_dir(self.temp_dir, phase="completion")
        self.assertFalse(result.ok)
        self.assertTrue(any("requires extra approval evidence" in error for error in result.errors))

    def test_accepts_approval_gated_dangerous_command_with_evidence(self) -> None:
        make_valid_case_package(self.temp_dir)
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
                "- 回传状态：complete",
                "- 回传状态：complete\n- 关键命令或动作：git reset --hard HEAD~1\n- 额外批准证据：user approved destructive reset in current thread",
            ),
            encoding="utf-8",
        )
        write(
            self.temp_dir / "approval-ledger.md",
            """# Approval Ledger

| branch | office | command | approval_status | approval_evidence | return |
|---|---|---|---|---|---|
| office-01 | 工部 | `git reset --hard` | present | user approved destructive reset in current thread | subagents/returns/subagent-return-office-01.md |
""",
        )
        write(
            self.temp_dir / "objection-review.md",
            """# 异议复核单

## 触发背景

- 触发原因：dangerous command + canonical update
- 输入材料：menxia-review.md, memorial-report.md, approval-ledger.md

## 复核摘要

- 重合问题：none
- 独有问题：none
- 误报：none
- 是否阻断：no
""",
        )
        result = validate_case_dir(self.temp_dir, phase="completion")
        self.assertTrue(result.ok, result.errors)

    def test_requires_approval_ledger_when_dangerous_command_exists(self) -> None:
        make_valid_case_package(self.temp_dir)
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
                "- 回传状态：complete",
                "- 回传状态：complete\n- 关键命令或动作：git reset --hard HEAD~1\n- 额外批准证据：user approved destructive reset in current thread",
            ),
            encoding="utf-8",
        )
        result = validate_case_dir(self.temp_dir, phase="completion")
        self.assertFalse(result.ok)
        self.assertTrue(any("approval-ledger.md is required" in error for error in result.errors))

    def test_rejects_real_subagent_dispatch_without_acceptance_criteria(self) -> None:
        make_valid_case_package(self.temp_dir)
        dispatch_path = self.temp_dir / "dispatch-order.md"
        dispatch_path.write_text(
            dispatch_path.read_text(encoding="utf-8").replace(
                "- 验收标准：scripts and tests pass with explicit return evidence\n",
                "",
            ),
            encoding="utf-8",
        )
        result = validate_case_dir(self.temp_dir, phase="completion")
        self.assertFalse(result.ok)
        self.assertTrue(any("missing substantive 验收标准" in error for error in result.errors))

    def test_rejects_ready_for_agent_when_branch_is_blocked(self) -> None:
        make_valid_case_package(self.temp_dir)
        dispatch_path = self.temp_dir / "dispatch-order.md"
        dispatch_path.write_text(
            dispatch_path.read_text(encoding="utf-8").replace("- blocked-by：none", "- blocked-by：user approval"),
            encoding="utf-8",
        )
        result = validate_case_dir(self.temp_dir, phase="completion")
        self.assertFalse(result.ok)
        self.assertTrue(any("blocked but dispatch is marked ready-for-agent" in error for error in result.errors))

    def test_rejects_unknown_dispatch_readiness_status(self) -> None:
        make_valid_case_package(self.temp_dir)
        dispatch_path = self.temp_dir / "dispatch-order.md"
        dispatch_path.write_text(
            dispatch_path.read_text(encoding="utf-8").replace(
                "- 派发就绪状态：ready-for-agent",
                "- 派发就绪状态：in-progress",
            ),
            encoding="utf-8",
        )
        result = validate_case_dir(self.temp_dir, phase="completion")
        self.assertFalse(result.ok)
        self.assertTrue(any("invalid 派发就绪状态" in error for error in result.errors))

    def test_requires_objection_review_for_dangerous_command_with_canonical_update(self) -> None:
        make_valid_case_package(self.temp_dir)
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
                "- 回传状态：complete",
                "- 回传状态：complete\n- 关键命令或动作：git reset --hard HEAD~1\n- 额外批准证据：approved",
            ),
            encoding="utf-8",
        )
        write(
            self.temp_dir / "approval-ledger.md",
            """# Approval Ledger

| branch | office | command | approval_status | approval_evidence | return |
|---|---|---|---|---|---|
| office-01 | 工部 | `git reset --hard` | present | approved | subagents/returns/subagent-return-office-01.md |
""",
        )
        result = validate_case_dir(self.temp_dir, phase="completion")
        self.assertFalse(result.ok)
        self.assertTrue(any("objection-review.md is required" in error for error in result.errors))


if __name__ == "__main__":
    unittest.main()

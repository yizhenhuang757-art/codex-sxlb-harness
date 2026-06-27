import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from subagent_dispatch import build_merge_summary, create_dispatch_bundle, record_subagent_return


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, text=True)


def make_dispatch_case(root: Path) -> None:
    write(
        root / "case.md",
        """# 立案单

## 基本信息

- 任务：Make sxlb a real subagent orchestra
- 用户目标：Turn real dispatch into executable packets
- 约束：Only touch scripts and tests
- 风险级别：medium
- 案卷路径：/tmp/example
- restart 目标：n/a

## 任务分类

- 任务类别：C
- 最小合法链路：太子 -> 尚书省 -> 单部执行 -> 门下复核 -> 回奏
- 当前建议链路：太子 -> 中书省 -> 门下省 -> 尚书省 -> 六部 -> 门下复核 -> 回奏
- 首办官署：工部
- 下一站：尚书省

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
- 多 agent 准入：pass
- 成本判断：clearly worth it
- delegation 可用性：available
- 本线办理理由：not-needed
- 返回审议点：门下复核
- 合流要求：merge required
- 合流摘要：subagents/merge-summary.md

## 官署分派

- 官署：工部
- 分支编号：office-01
- 任务：Implement the script layer
- 所有权：scripts/
- 共享只读：tests/
- 禁写范围：protocols/
- 可写范围：scripts/
- 真实触达审计：required
- 危险命令策略：no destructive commands
- 需额外批准动作：none
- 整合者：工部
- 允许技能：python
- 禁止越权：do not edit protocols
- 分支执行：real-subagent
- 工作包：subagents/subagent-work-packet-office-01.md
- 回传物：subagents/returns/subagent-return-office-01.md
- 升级条件：boundary conflict

- 官署：礼部
- 分支编号：office-local-libu
- 任务：Prepare user-facing summary copy
- 所有权：response wording
- 共享只读：scripts/
- 禁写范围：protocols/, tests/
- 整合者：礼部
- 允许技能：writing
- 禁止越权：do not claim unrun tests
- 分支执行：local-office
- 工作包：n/a
- 回传物：local notes
- 升级条件：claim depends on unrun verification

- 官署：吏部
- 分支编号：office-02
- 任务：Add verification coverage
- 所有权：tests/
- 共享只读：scripts/
- 禁写范围：reports/
- 整合者：工部
- 允许技能：python, unittest
- 禁止越权：do not edit reports
- 分支执行：real-subagent
- 工作包：subagents/subagent-work-packet-office-02.md
- 回传物：subagents/returns/subagent-return-office-02.md
- 升级条件：test scope unclear

## 双轨附记

- 文线：礼部处理回奏用语
- 武线：工部与吏部补脚本和测试
- 合流点：门下复核
- 合流负责：工部
""",
    )


class SubagentDispatchTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="sxlb-subagent-"))
        make_dispatch_case(self.temp_dir)

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir)

    def test_create_dispatch_bundle_only_materializes_real_subagent_packets(self) -> None:
        created = create_dispatch_bundle(self.temp_dir)
        manifest_path = self.temp_dir / "subagents" / "manifest.json"
        self.assertIn(manifest_path, created)
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertEqual([packet["office"] for packet in manifest["packets"]], ["工部", "吏部"])
        packet_path = self.temp_dir / "subagents" / "subagent-work-packet-office-01.md"
        self.assertTrue(packet_path.exists())
        packet_text = packet_path.read_text(encoding="utf-8")
        self.assertIn("分支编号：office-01", packet_text)
        self.assertIn("所属官署：工部", packet_text)
        self.assertIn("可写范围：scripts/", packet_text)
        self.assertIn("禁写范围：protocols/", packet_text)
        self.assertIn("真实触达审计：required", packet_text)
        self.assertIn("touched_files.py --repo", packet_text)
        self.assertIn("需额外批准动作：none", packet_text)

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        packet = next(packet for packet in manifest["packets"] if packet["packet_id"] == "office-01")
        self.assertEqual(packet["actual_touched_audit"], "required")

    def test_create_dispatch_bundle_generates_heavy_dispatch_state_for_gate_pass(self) -> None:
        created = create_dispatch_bundle(self.temp_dir)
        state_path = self.temp_dir / "heavy-dispatch-state.md"
        self.assertIn(state_path, created)
        state_text = state_path.read_text(encoding="utf-8")
        self.assertIn("- heavy layer：active", state_text)
        self.assertIn("- 启动依据：多 agent 准入：pass; 真实派发：yes", state_text)
        self.assertIn("- 分支编号：office-01", state_text)
        self.assertIn("- 官署：工部", state_text)
        self.assertIn("- 状态：queued", state_text)
        self.assertIn("- 工作包：subagents/subagent-work-packet-office-01.md", state_text)
        self.assertIn("- 回传物：pending", state_text)

    def test_record_subagent_return_updates_heavy_dispatch_state(self) -> None:
        create_dispatch_bundle(self.temp_dir)
        record_subagent_return(
            self.temp_dir,
            packet_id="office-01",
            status="completed",
            summary="Implemented the dispatch script",
            touched_artifacts=["scripts/subagent_dispatch.py"],
            verification="unittest passed",
            risks="none",
            next_step="merge",
        )
        state_text = (self.temp_dir / "heavy-dispatch-state.md").read_text(encoding="utf-8")
        self.assertIn("- 分支编号：office-01", state_text)
        self.assertIn("- 状态：returned", state_text)
        self.assertIn("- 回传物：subagents/returns/subagent-return-office-01.md", state_text)
        self.assertIn("- 验证状态：pass", state_text)
        self.assertIn("- 分支编号：office-02", state_text)
        self.assertIn("- 状态：queued", state_text)

    def test_record_subagent_return_appends_execution_observation(self) -> None:
        create_dispatch_bundle(self.temp_dir)
        record_subagent_return(
            self.temp_dir,
            packet_id="office-01",
            status="completed",
            summary="Implemented the dispatch script",
            touched_artifacts=["scripts/subagent_dispatch.py"],
            verification="unittest passed",
            risks="none",
            next_step="merge",
        )
        observations_path = self.temp_dir / "execution-observations.jsonl"
        self.assertTrue(observations_path.exists())
        observations = [
            json.loads(line)
            for line in observations_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        self.assertEqual(len(observations), 1)
        observation = observations[0]
        self.assertEqual(observation["office"], "工部")
        self.assertEqual(observation["source"], "subagent_dispatch.record")
        self.assertEqual(observation["event"], "subagent-return-recorded")
        self.assertEqual(observation["evidence"]["packet_id"], "office-01")
        self.assertEqual(observation["evidence"]["status"], "completed")
        self.assertEqual(observation["evidence"]["return_file"], "subagents/returns/subagent-return-office-01.md")
        self.assertEqual(observation["evidence"]["verification"], "unittest passed")
        self.assertEqual(observation["promote_to"], "learning-candidates.jsonl")

    def test_record_subagent_return_updates_manifest_and_creates_return_file(self) -> None:
        create_dispatch_bundle(self.temp_dir)
        return_path = record_subagent_return(
            self.temp_dir,
            packet_id="office-02",
            status="completed",
            summary="Added unittest coverage for the new script layer",
            touched_artifacts=["/tmp/example/tests/test_subagent_dispatch.py"],
            verification="unittest passed",
            risks="none",
            next_step="merge back to 工部",
        )
        self.assertTrue(return_path.exists())
        self.assertIn("Added unittest coverage", return_path.read_text(encoding="utf-8"))
        self.assertEqual(return_path.name, "subagent-return-office-02.md")

        manifest = json.loads((self.temp_dir / "subagents" / "manifest.json").read_text(encoding="utf-8"))
        packet = next(packet for packet in manifest["packets"] if packet["packet_id"] == "office-02")
        self.assertEqual(packet["return_status"], "completed")
        self.assertIn("Added unittest coverage", packet["return_summary"])

    def test_record_subagent_return_can_generate_actual_touched_files_evidence(self) -> None:
        git(self.temp_dir, "init")
        git(self.temp_dir, "config", "user.email", "sxlb@example.test")
        git(self.temp_dir, "config", "user.name", "SXLB Test")
        git(self.temp_dir, "add", "case.md", "dispatch-order.md")
        git(self.temp_dir, "commit", "-m", "initial")
        write(self.temp_dir / "scripts" / "subagent_dispatch.py", "changed\n")

        create_dispatch_bundle(self.temp_dir)
        return_path = record_subagent_return(
            self.temp_dir,
            packet_id="office-01",
            status="completed",
            summary="Implemented the dispatch script",
            touched_artifacts=["scripts/subagent_dispatch.py"],
            verification="unittest passed",
            risks="none",
            next_step="merge",
            touched_files_repo=self.temp_dir,
        )

        touched_path = self.temp_dir / "subagents" / "returns" / "touched-files-office-01.txt"
        self.assertTrue(touched_path.exists())
        self.assertIn("scripts/subagent_dispatch.py", touched_path.read_text(encoding="utf-8"))
        return_text = return_path.read_text(encoding="utf-8")
        self.assertIn("真实触达清单：subagents/returns/touched-files-office-01.txt", return_text)

        manifest = json.loads((self.temp_dir / "subagents" / "manifest.json").read_text(encoding="utf-8"))
        packet = next(packet for packet in manifest["packets"] if packet["packet_id"] == "office-01")
        self.assertEqual(packet["actual_touched_file"], "subagents/returns/touched-files-office-01.txt")

    def test_record_subagent_return_can_include_extra_approval_evidence(self) -> None:
        create_dispatch_bundle(self.temp_dir)
        return_path = record_subagent_return(
            self.temp_dir,
            packet_id="office-01",
            status="completed",
            summary="Performed approved reset",
            touched_artifacts=["scripts/tool.py"],
            verification="manual verification passed",
            risks="none",
            next_step="merge",
            approval_evidence="user approved dangerous command in current thread",
        )
        return_text = return_path.read_text(encoding="utf-8")
        self.assertIn("额外批准证据：user approved dangerous command in current thread", return_text)

        manifest = json.loads((self.temp_dir / "subagents" / "manifest.json").read_text(encoding="utf-8"))
        packet = next(packet for packet in manifest["packets"] if packet["packet_id"] == "office-01")
        self.assertEqual(packet["approval_evidence"], "user approved dangerous command in current thread")

    def test_merge_summary_reports_completed_and_pending_packets(self) -> None:
        create_dispatch_bundle(self.temp_dir)
        record_subagent_return(
            self.temp_dir,
            packet_id="office-01",
            status="completed",
            summary="Implemented the dispatch script",
            touched_artifacts=["/tmp/example/scripts/subagent_dispatch.py"],
            verification="manual run ok",
            risks="needs integration review",
            next_step="wait for 吏部 branch",
        )
        summary_path = build_merge_summary(self.temp_dir, force=True)
        summary = summary_path.read_text(encoding="utf-8")
        self.assertIn("已回传分支：1/2", summary)
        self.assertIn("是否可进入门下复核：no", summary)
        self.assertIn("待补分支：office-02", summary)


if __name__ == "__main__":
    unittest.main()

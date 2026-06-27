# 派令

## 派发信息

- 当前阶段：<stage>
- 拓扑：<single-thread|serial|parallel|dual-track>
- 执行方式：<local-office|real-subagent>
- 真实派发：<yes|no>
- 能力召回：<semantic_keywords; retained clan_candidates, family_candidates, and skill_bundles from recall_capabilities.py; execution still follows allowed 六部 skills and concrete SKILL.md triggers>
- 多 agent 准入：<pass|fail|n/a>
- 准入理由：<one-line judgment or n/a>
- 成本判断：<clearly worth it|not worth it|uncertain|n/a>
- delegation 可用性：<available|unavailable>
- 本线办理理由：<required when a delegable branch stays local>
- 派发就绪状态：<ready-for-agent|ready-for-human|needs-info|blocked|n/a>
- readiness 规则：<exactly one status; use needs-info for missing facts, ready-for-human for user decision, blocked for external dependency>
- 返回审议点：<review return points>
- 合流要求：<merge required or not>
- 合流摘要：<merge-summary.md or n/a>
- 执行预算：<tool/turn/time budget or n/a>
- 修复循环上限：<max retry/fix loops before recall or review>
- 预算超限处理：<return to 尚书省|门下审议|user decision>

## 官署分派

Repeat this block once per assigned office:

- 官署：<office>
- 分支编号：<branch id>
- 任务：<owned task>
- 切片类型：<端到端薄切片 (vertical slice)|support slice|research slice|verification slice|coordination slice|n/a>
- 交互模式：<AFK|HITL + decision point|n/a>
- blocked-by：<dependency|none|n/a>
- 验收标准：<observable acceptance criteria or n/a>
- 所有权：<owned files/artifacts/decision scope>
- 共享只读：<shared context or none>
- 禁写范围：<forbidden scope>
- 可写范围：<writable files/artifacts/decision scope>
- 真实触达审计：<required|not required>
- 危险命令策略：<dangerous command policy>
- 需额外批准动作：<actions requiring extra approval>
- 整合者：<owner or n/a>
- 允许技能：<canonical skills>
- 禁止越权：<boundary reminder>
- 分支执行：<local-office|real-subagent>
- 工作包：<subagent-work-packet-<branch>.md or n/a>
- 回传物：<subagent-return-<branch>.md or local notes>
- 升级条件：<when this branch must stop and return>

## 双轨附记

- 文线：<assignment or n/a>
- 武线：<assignment or n/a>
- 合流点：<merge checkpoint or n/a>
- 合流负责：<merge owner or n/a>

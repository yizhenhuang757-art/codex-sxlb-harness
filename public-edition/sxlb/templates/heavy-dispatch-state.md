# Heavy Dispatch State

## State Header

- 案件编号：<case id>
- heavy layer：<inactive|active|paused|closed|recalled>
- 启动依据：<dispatch-order.md admission result>
- 状态来源：<manual|subagents/manifest.json|other>
- 合流负责：<merge owner>
- 最后更新：<timestamp>

## Branches

Repeat once per real branch:

- 分支编号：<branch id>
- 官署：<office>
- 执行环境：<shared-repo|worktree:path|read-only|other>
- 可写范围：<write scope>
- 状态：<queued|running|blocked|returned|merged|recalled|closed>
- 工作包：<subagent-work-packet-<branch>.md>
- 回传物：<subagent-return-<branch>.md or pending>
- 验证状态：<pending|pass|fail|n/a>
- 合流状态：<pending|merged|conflict|n/a>
- 最后实质更新：<timestamp or note>

## Shutdown

- 关闭状态：<not-started|closed|paused|recalled>
- 未闭合分支：<none or branch ids>
- 门下复核输入：<dispatch + packets + returns + merge + verification>

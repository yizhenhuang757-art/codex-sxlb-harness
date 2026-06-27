# 立案单

## 基本信息

- 案件编号：<case id>
- 任务：<task title>
- 用户目标：<goal>
- 约束：<constraints>
- 上下文入口：<restart/catalog/source files to read first>
- 风险级别：<low|medium|high>
- 案卷路径：<worklog path>
- 案卷重量：<lightweight|full>
- restart 目标：<restart note or n/a>
- 能力召回：<semantic_keywords; 0-2 clan_candidates; 0-3 family_candidates; retained skill_bundles from recall_capabilities.py, or none>

## 任务分类

- 任务类别：<A|B|C|D>
- 最小合法链路：<legal minimum chain>
- 当前建议链路：<current legal chain>
- 首办官署：<first owning office>
- 下一站：<next office>
- 真实派发策略：<local-only|conditional-subagent|real-subagent-required>
- 合流负责人：<merge owner or n/a>

## 立案备注

- 关键未知：<unknowns>
- 需要用户确认：<yes/no + note>
- 可能更新的 canonical：<docs or none>

## 起居郎候补

Optional; use `none` when no future-facing vault documentation changed.

- [ ] target: <file or surface, or none>
  reason: <why future human-facing docs may need a delta>
  source: <case artifact or user-named evidence>
  level: <none|light|manual|report|archive>

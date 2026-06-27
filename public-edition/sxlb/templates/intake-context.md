# 太子上下文入口

用途：按需压缩太子入口上下文。默认案卷应优先使用 `case.md` 的 `上下文入口` 字段；只有 C/D 复杂案、真实派发、跨案卷转交或长线程压缩时才单独生成本文件。

## 必填字段

- 案由：<one-line case reason>
- 用户目标：<user goal in current words>
- 约束：<known constraints>
- 上下文入口：<files or restart/catalog pointers to read first>
- 下一站：<中书省|尚书省|other>
- 关键未知：<unknowns or none>
- 不做什么：<non-goals>

## 太子边界

- 太子只记录案由、入口、路由和退出触发。
- 太子不写 PRD、ADR、决策树、实现方案、验收标准或 canonical 决策。

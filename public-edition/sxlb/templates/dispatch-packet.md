# 尚书上下文包

用途：按需压缩派发上下文。默认案卷应优先使用 `dispatch-order.md` 的官署分派字段；只有 C/D 复杂案、真实派发、跨案卷转交或长线程压缩时才单独生成本文件。

## 分支

- 官署：<office>
- 任务：<owned task>
- readiness：<ready-for-agent|ready-for-human|needs-info|blocked|n/a>
- 共享只读：<read bundle>
- 可写范围：<writable files/artifacts/decision scope>
- 禁写范围：<forbidden scope>
- 回传物：<return artifact>

## 派发边界

- 尚书省切上下文包和 ownership，不重新拟制方案。
- 缺上下文时标记 `needs-info`，不要让执行部门自行扩展成 mini research。

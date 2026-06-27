# Session Dry Run

## Scenario

The user wants to build a small framework feature and asks the assistant to work in `sxlb` mode.

## Transcript

### 1. User enters `sxlb`

```text
User: sxlb
Assistant: Entering sxlb mode for this thread. I will route the task through the 三省六部 framework until you explicitly exit.
```

### 2. User gives a task

```text
User: Build a status summary widget for this tool and make sure it updates correctly.
Assistant (太子): Filing the case.
```

### 3. Case filing and classification

```md
# 立案单

- 案件编号：status-summary-widget
- 任务：status summary widget
- 用户目标：add a widget and verify correct updates
- 约束：keep the change bounded
- 风险级别：medium
- 任务类别：C
- 当前建议链路：太子 -> 中书省 -> 门下省 -> 尚书省 -> 六部 -> 门下省 -> 回奏
- 下一站：中书省
- 真实派发策略：conditional-subagent
- 合流负责人：尚书省
```

### 4. Planning and review

```md
# 中书方案

- 目标：add the widget and verify update behavior
- 不做什么：no redesign of the surrounding page
- 成功标准：widget renders and update behavior is verified
- 主任务：implement widget, connect state, verify updates
- 路由建议：C
- 主要官署：工部, 刑部
```

```md
# 审议单

- 结论：通过
- 主要依据：scope is bounded and verification is explicit
- 返回状态：尚书派发
- 返回官署：尚书省
```

### 5. Status board appears

```md
# 朝堂状态

任务：status summary widget
模式：SXLB
当前状态：尚书派发
运行态：review
案卷：$SXLB_CASE_ROOT/status-summary-widget/
事件簿：active
分流状态：未开始

## 当前链路
- 太子：已立案
- 中书省：已提交方案
- 门下省：审议通过
- 尚书省：待派发
- 六部：n/a

## 已派发
- none

## 记录去向
- 案卷：$SXLB_CASE_ROOT/status-summary-widget/
- canonical：none
- restart：none

## 待决问题
- 工部与刑部是否串行

## 可干预命令
- `继续`
- `暂停`
- `恢复`
- `会审`
- `重审`
- `录案`
- `召回 <某部>`
- `并行 <某部> <某部>`
- `退朝`
```

### 6. User intervenes

```text
User: 召回 刑部，先串行，不要并行。
Assistant (尚书省): Updated dispatch. 工部 goes first, 刑部 verifies after implementation returns.
```

### 7. Dispatch order

```md
# 派令

- 当前阶段：尚书派发
- 拓扑：serial
- 执行方式：real-subagent
- 真实派发：yes
- delegation 可用性：available
- 本线办理理由：n/a
- 返回审议点：after merge summary
- 合流要求：merge required
- 合流摘要：merge-summary.md

## 官署分派

- 官署：工部
- 分支编号：impl
- 任务：build the widget and wire update logic
- 所有权：widget files and local state wiring
- 共享只读：existing page layout
- 禁写范围：routing docs and unrelated layout files
- 整合者：尚书省
- 允许技能：superpowers:test-driven-development
- 禁止越权：do not widen scope
- 分支执行：real-subagent
- 工作包：subagent-work-packet-impl.md
- 回传物：subagent-return-impl.md
- 升级条件：stop if update behavior requires scope expansion

- 官署：刑部
- 分支编号：verify
- 任务：verify update behavior after implementation handoff
- 所有权：verification plan and fresh test evidence
- 共享只读：工部提交的实现结果, widget requirements
- 禁写范围：implementation files
- 整合者：尚书省
- 允许技能：superpowers:systematic-debugging, superpowers:verification-before-completion
- 禁止越权：do not take over implementation
- 分支执行：real-subagent
- 工作包：subagent-work-packet-verify.md
- 回传物：subagent-return-verify.md
- 升级条件：stop if implementation fix is required

## 双轨附记

- 文线：n/a
- 武线：n/a
- 合流点：merge both branch returns before 门下审议
- 合流负责：尚书省
```

### 8. Work packets and returns appear

```md
# 子代理工作包

- 案件编号：status-summary-widget
- 分支编号：impl
- 所属官署：工部
- 可写范围：widget files and state wiring
- 共享只读：requirements note and existing page structure
- 禁写范围：verification notes and unrelated layout
- 返回物：subagent-return-impl.md
```

```md
# 子代理回传物

- 案件编号：status-summary-widget
- 分支编号：impl
- 所属官署：工部
- 回传状态：needs-merge
- 触达文件/产物：widget component, state hook
- 是否越权：no
- 建议下一步：send to verification branch and then merge
```

```md
# 合流摘要

- 案件编号：status-summary-widget
- 合流负责人：尚书省
- 参与分支：impl, verify
- 合流后的主张：implementation and fresh verification are both present
- 剩余风险：edge-case regression coverage is still future work
- 请求结论：allow review
```

### 9. Final memorial

```md
# 回奏

- 任务：status summary widget
- 使用链路：太子 -> 中书省 -> 门下省 -> 尚书省 -> 工部 -> 刑部 -> 门下省 -> 回奏
- 当前结果：completed
- 关键决策：used serial execution instead of parallel execution
- 验证证据：fresh widget update check completed by 刑部
- 剩余风险：edge cases still depend on future regression coverage
- 案卷归档：status-summary-widget worklog updated
- canonical 更新：none
- restart 更新：none
- 顺的地方：scope stayed bounded through review and dispatch
- 卡的地方：initial dispatch order needed user correction
- 返工点：dispatch was revised before execution
- 下次应升级的规则：worker packet defaults could be even smaller
- 推荐动作：keep sxlb mode active for the next complex task or exit if ordinary mode is enough
```

## What This Dry Run Demonstrates

- explicit `sxlb` activation
- task classification
- visible status board as mandatory governed surface
- optional `会审` escalation for contested decisions
- user intervention through `召回`
- packet-backed real subagent branches
- merge summary before `门下省`
- final memorial plus records split and retrospective

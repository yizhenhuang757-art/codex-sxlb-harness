# 异议复核协议

## 目的

在高风险结案前提供低成本第二意见，不把常规案件拖成会审。

## 触发条件

默认仅在以下任一条件触发：

- real-subagent 回传出现危险命令，且 `memorial-report.md` 标记了实质 `canonical 更新`
- 门下省显式要求补做异议复核

## 输入材料

- `menxia-review.md`
- `approval-ledger.md`（如存在危险命令）
- `memorial-report.md`

## 最小输出

`objection-review.md` 至少包含：

- 重合问题（与门下复核一致）
- 独有问题（新发现）
- 误报（可忽略项）
- 是否阻断（yes/no）

## 结案关系

若触发条件满足而 `objection-review.md` 缺失，`sxlb_guard.py` 应阻断 completion。

# 朝堂状态

使用规则：在 `sxlb` 模式下，凡属规划、执行、审议、派发、回奏、退朝清算中的任一回合，回复开头都应先贴本板；只有闲聊、退朝清算完成后的最终退出确认、或用户明确要求本回合隐藏时可省略。发送前先做输出自检：若仍处于 active `sxlb` 且没有允许省略理由，第一行必须是 `朝堂状态`。面板形态由 `scripts/status_board.py` 根据状态机分流；普通回复以 state/body packet 交给 `sxlb_reply.py --body-stdin` 作为 single generated-reply outlet，AI 不直接起草本板字段。Do not introduce unlisted historical court offices as board fields or owners; unknown office-like fields fail board validation. 可用 `scripts/response_board_check.py` 校验草稿；它会检查开头、`## 回奏`、压缩面板必备字段和固定干预命令。一般情况下，整条回复应分成两部分：`朝堂状态` 与 `回奏`。本板只承担状态展示，正式答复应另起 `## 回奏`。

默认显示紧凑版。压缩面板有五类：默认紧凑版、太子面板、中书面板、门下面板、尚书面板；六部执行使用默认紧凑版。`scripts/status_board.py` 按状态自动选择：`待立案` -> 太子面板，`中书拟制` -> 中书面板，`门下审议`/`门下复核` -> 门下面板，`尚书派发` -> 尚书面板，`六部执行` -> 默认紧凑版。只有在下面情况使用完整版：首次进入 `sxlb`、建立或切换案卷、`中书省`给出正式方案、`门下省`正式审议或封驳、`尚书省`正式派发、真实 subagent 并行派发、采风进入多分支外部证据包、进入 `待分流`、进入 `退朝清算`、结案回奏、用户输入 `事件簿` / `重审` / `会审` / `录案`、或出现 blocked、风险、权限、证据不足、分支冲突。

面板不得作为唯一记录源。面板只显示当前视图；状态、决策、证据、派发、审议和回奏必须写入对应案卷产物：`case.md`、`zhongshu-plan.md`、`menxia-review.md`、`dispatch-order.md`、`event-ledger.md`、`memorial-report.md`，或对应的外部证据包。

分层展示规则：不要通过默认隐藏或砍掉 `朝堂状态` 来处理复杂度。保留面板作为高层状态投影；用户可见回答放在 `回奏`；耐久事实进入案卷；执行证据进入 `event-ledger.md`、`artifact-registry.md`、`verification.md`、`merge-summary.md` 或分支 return；不满意追因进入 `dissatisfaction-diagnostic.md` 或按同样标题内联说明。

## 默认紧凑版

任务：<task title>
状态：<当前状态> / <运行态>
链路：<太子 -> 中书省 -> 门下省 -> 尚书省 -> 当前六部或 n/a>
案卷状态：<无|案卷 名|多案卷 主=名 参=名,名|锚点 名|案卷+锚点 案卷名/锚点名|待补|需检索>[；钩子 名,名]
采风：<n/a|待采证|采证中|证据包待审|已入方案>
待决：<open question or none>
干预：`继续` `暂停` `会审` `重审` `录案` `事件簿` `侍讲官 <问题>` `国史馆` `翰林院` `起居郎` `退朝`

## 太子面板

任务：<task title>
太子：立案 / <active|blocked|done>
分类：<A|B|C|D|待定>
首办：<office or n/a>
案卷状态：<无|案卷 名|多案卷 主=名 参=名,名|锚点 名|案卷+锚点 案卷名/锚点名|待补|需检索>[；钩子 名,名]
待决：<intake question or none>
干预：`继续` `暂停` `会审` `重审` `录案` `事件簿` `侍讲官 <问题>` `国史馆` `翰林院` `起居郎` `退朝`

## 中书面板

任务：<task title>
中书：拟制 / <active|blocked|done>
方案：<草拟中|待审|已交门下>
决策树：<open|closed|n/a>
案卷状态：<无|案卷 名|多案卷 主=名 参=名,名|锚点 名|案卷+锚点 案卷名/锚点名|待补|需检索>[；钩子 名,名]
采风：<n/a|待采证|采证中|证据包待审|已入方案>
产物：`zhongshu-plan.md`
待决：<planning question or none>
干预：`继续` `暂停` `会审` `重审` `录案` `事件簿` `侍讲官 <问题>` `国史馆` `翰林院` `起居郎` `退朝`

## 门下面板

任务：<task title>
门下：<none|审议中|通过|封驳|补证|复核中|复核通过|复核封驳|复核补证|done×N>
对象：<方案|派令|完成包|证据包>
结论：<待审|通过|封驳|补证后再审>
问题：<证据|边界|复杂度|路由|none>
案卷状态：<无|案卷 名|多案卷 主=名 参=名,名|锚点 名|案卷+锚点 案卷名/锚点名|待补|需检索>[；钩子 名,名]
产物：`menxia-review.md`
待决：<review question or none>
干预：`继续` `暂停` `会审` `重审` `录案` `事件簿` `侍讲官 <问题>` `国史馆` `翰林院` `起居郎` `退朝`

## 会审提示

仅在已进入 `会审` 时显示：

会审干预：`六帽`

## 尚书面板

任务：<task title>
尚书：派发 / <active|blocked|done>
拓扑：<single-thread|serial|parallel|dual-track>
派发：<local-office|real-subagent|none>
readiness：<ready-for-agent|ready-for-human|needs-info|blocked|n/a>
合流：<n/a|待合流|已合流>
案卷状态：<无|案卷 名|多案卷 主=名 参=名,名|锚点 名|案卷+锚点 案卷名/锚点名|待补|需检索>[；钩子 名,名]
产物：`dispatch-order.md`
待决：<dispatch question or none>
干预：`继续` `暂停` `会审` `重审` `录案` `事件簿` `侍讲官 <问题>` `国史馆` `翰林院` `起居郎` `退朝`

## 完整版

任务：<task title>
模式：SXLB
当前状态：<待立案|中书拟制|门下审议|尚书派发|六部执行|门下复核|待回奏|待分流|退朝清算|已回奏|已暂停|已中止>
运行态：<active|paused|blocked|review|done>
案卷状态：<无|案卷 名|多案卷 主=名 参=名,名|锚点 名|案卷+锚点 案卷名/锚点名|待补|需检索>[；钩子 名,名]
案卷：<worklog path or n/a>
事件簿：<active|complete|n/a>
分流状态：<未开始|案卷已归档|canonical 已更新|restart 已更新|完成>
采风：<n/a|待采证|采证中|证据包待审|已入方案>

## 当前链路

- 太子：<status>
- 中书省：<status or n/a>
- 门下省：<status or n/a>
- 尚书省：<status or n/a>
- 六部：<status or n/a>

## 已派发

- <office>: <task or none>

## 记录去向

- 案卷：<worklog files or none>
- canonical：<target docs or none>
- restart：<target note or none>

## 待决问题

- <open question or none>

## 可干预命令

- `继续`
- `暂停`
- `恢复`
- `会审`
- `重审`
- `追因`
- `诊断`
- `录案`
- `召回 <某部>`
- `并行 <某部> <某部>`
- `事件簿`
- `侍讲官 <问题>`
- `国史馆`
- `翰林院`
- `起居郎`
- `退朝`

## 回奏

<user-facing answer>

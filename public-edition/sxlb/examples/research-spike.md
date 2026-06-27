# Research Spike Example

## Task

Compare two multi-agent workflow architectures, build one small prototype, and recommend which direction to adopt.

## Task Classification

- class: `D`
- reason: strategy and engineering feasibility both matter, so `文线` and `武线` must run before the final recommendation

## Office Chain

- `太子`: files the case as `D`
- `中书省`: produces a split plan with `文线` and `武线`
- `门下省`: checks whether the split and merge criteria are sound
- `尚书省`: issues one dual-track real-subagent dispatch order
- `礼部` subagent on `文线`: turns the comparison questions into a readable recommendation memo
- `工部` subagent on `武线`: builds the prototype and records feasibility findings
- merge owner: consolidates both branch returns into one decision surface
- `门下省`: reviews the packets, returns, and merge summary and asks for more evidence if needed
- `回奏`: recommends the direction and records prototype evidence

## Intervention Points

- after `中书省`: user may say `重审` if the split is weak
- at dispatch: user may say `并行 礼部 工部` or `召回 <某部>`
- after merge: user may ask `门下省` to `重审` if the evidence package still feels thin
- when research and prototype point in different directions: user may call `会审`

## Visible Artifacts

- `立案单`
- `中书方案`
- dual-track `派令`
- `subagent-work-packet-wen.md`
- `subagent-return-wen.md`
- `subagent-work-packet-wu.md`
- `subagent-return-wu.md`
- `merge-summary.md`
- `朝堂状态`
- merge-focused `审议单`
- `回奏`

### Minimal Artifact Samples

- `立案单`
  - task: compare two workflow architectures and test one prototype
  - class: `D`
  - next office: `中书省`
- `中书方案`
  - `文线`: architecture comparison memo
  - `武线`: one prototype proving the riskiest integration
  - merge rule: `门下省` reviews both outputs together before recommendation
- `派令`
  - `礼部`: produce the comparison memo for `文线`
  - `工部`: build the prototype for `武线`
  - both branches: `real-subagent`
  - merge checkpoint: combined evidence package returns to `门下省`
- `subagent-work-packet-wen.md`
  - writable scope: comparison memo only
  - read bundle: case summary, evaluation criteria, selected references
  - forbidden scope: prototype code and implementation claims
- `subagent-return-wen.md`
  - output: recommendation memo with tradeoff table
  - unresolved issue: one assumption depends on prototype evidence
- `subagent-work-packet-wu.md`
  - writable scope: prototype branch and feasibility notes
  - read bundle: riskiest integration target, success criteria
  - forbidden scope: final strategy recommendation
- `subagent-return-wu.md`
  - output: prototype plus feasibility note
  - unresolved issue: one integration path remains costly
- `merge-summary.md`
  - integrated claim: architecture A is strategically cleaner, but architecture B now has a proven integration path
  - review ask: decide whether feasibility proof outweighs structural complexity
- `朝堂状态`
  - current state: `六部执行`
  - active offices: `礼部`, `工部`
  - pending merge review: yes
- `审议单`
  - verdict: `补证后再审` if either track lacks usable evidence
  - return state: `门下审议`
  - return office: `门下省`

## State Progression

- `待立案 -> 中书拟制 -> 门下审议 -> 尚书派发 -> 六部执行 -> 门下审议 -> 待回奏 -> 待分流 -> 已回奏`

## Final Memorial Structure

- task summary
- chain used
- packet-backed branch boundaries
- `文线` findings
- `武线` findings
- merge summary judgment
- merge decision
- evidence and open risks
- recommended next move

# Engineering Feature Example

## Task

Build a new workflow panel for a local tool and verify that the panel state persists correctly.

## Task Classification

- class: `C`
- reason: multi-step engineering work with planning, implementation, verification, and review

## Office Chain

- `太子`: opens the case and classifies the task as `C`
- `中书省`: writes a plan for UI work, state persistence, and verification
- `门下省`: checks scope, review points, and verification requirements
- `尚书省`: issues a real-subagent dispatch with one implementation packet and one verification packet
- `工部` subagent: implements the workflow panel and persistence wiring inside its owned file boundary
- `刑部` subagent: verifies persistence behavior and regressions against the returned implementation evidence
- merge owner: combines both branch returns into one review package
- `门下省`: reviews the dispatch, branch returns, and merge summary together
- `回奏`: summarizes delivery and remaining risks

## Intervention Points

- after `中书省`: user may say `重审` or `退朝`
- when scope, UX, and verification priorities conflict: user may call `会审`
- before `尚书省` dispatch: user may say `召回 <某部>` or `并行 <某部> <某部>`
- during execution: user may say `召回 工部` or `暂停`

## Visible Artifacts

- `立案单`
- `中书方案`
- `审议单`
- `派令`
- `subagent-work-packet-impl.md`
- `subagent-return-impl.md`
- `subagent-work-packet-verify.md`
- `subagent-return-verify.md`
- `merge-summary.md`
- `朝堂状态`
- `回奏`

### Minimal Artifact Samples

- `立案单`
  - task: workflow panel with persistence
  - class: `C`
  - next office: `中书省`
- `中书方案`
  - route: `C`
  - topology recommendation: serial `工部 -> 刑部`
  - review question: persistence verification must use fresh evidence
- `审议单`
  - verdict: `通过`
  - return state: `尚书派发`
  - return office: `尚书省`
- `派令`
  - `工部`: build panel UI and persistence wiring
  - `刑部`: run persistence verification after implementation handoff
  - branch mode: both marked `real-subagent`
  - merge owner: `尚书省`
- `subagent-work-packet-impl.md`
  - writable scope: panel component and persistence wiring files only
  - forbidden scope: unrelated layout code and release notes
  - required return: touched files plus implementation risk note
- `subagent-return-impl.md`
  - completed: panel rendering and persistence wiring
  - open risk: migration edge case still unverified
- `subagent-work-packet-verify.md`
  - read bundle: impl return plus changed files
  - forbidden scope: no product redesign, no implementation takeover
  - required return: fresh persistence evidence and regression note
- `subagent-return-verify.md`
  - evidence: fresh persistence check passed on the modified panel
  - open issue: one edge case should be covered later
- `merge-summary.md`
  - mergeable claim: panel shipped with fresh persistence verification
  - still-open risk: long-tail regression coverage remains future work
- `朝堂状态`
  - current state: `六部执行`
  - active offices: `工部`, `刑部`
  - next review point: `门下审议`

## State Progression

- `待立案 -> 中书拟制 -> 门下审议 -> 尚书派发 -> 六部执行 -> 门下审议 -> 待回奏 -> 待分流 -> 已回奏`

## Final Memorial Structure

- task summary
- chain used
- packet-backed branch scope
- branch return evidence
- merge decision
- key decisions
- verification evidence
- remaining risks
- next recommended move

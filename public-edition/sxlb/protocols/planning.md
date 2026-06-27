# Planning Protocol

## Purpose

Define how `中书省` converts a filed case into a governed plan.

## Inputs

- `立案单`
- project context
- user constraints
- relevant source material

## Outputs

- `中书方案`
- PRD-shaped clarification block only when the task has product, workflow, or engineering ambiguity
- office/skill mapping
- routing recommendation
- explicit review questions for `门下省`
- records routing recommendation

## Planning Rules

- Restate scope before decomposing work.
- Surface unknowns and risks instead of hiding them in execution.
- Before decomposing, name any `未声明假设` that would materially affect the route, verification, or write boundary.
- If the plan depends on current external information, open `采风`: write a small question tree and request an `外部证据包` before settling the plan.
- Close the planning `决策树` before dispatch when unresolved user choices, HITL checkpoints, or branch-blocking unknowns would affect execution.
- Normalize `领域语言` and project terms before assigning multi-office or multi-agent work.
- Check relevant ADR or ADR-like decision records when architecture, integration, or long-lived workflow boundaries are affected; otherwise mark this as `n/a`.
- For ambiguous engineering work, shape the `中书方案` like a compact PRD: problem, users/stakeholders, non-goals, acceptance criteria, testing decisions, and out-of-scope notes.
- Before recommending 架构改造, name the observed 真实摩擦 it solves; if the friction is only hypothetical, keep the plan to investigation or a smaller local change.
- Keep the plan free of `不必要复杂度`: prefer the smallest chain, office set, and artifact set that still satisfies the legal checkpoints.
- State the `改动边界` for file-editing or framework-changing work, including explicit non-goals and areas that must not be touched opportunistically.
- For each substantive step, pair `步骤 -> 验证方式` so execution can close against observable evidence rather than intention.
- State `测试决策`: what must be tested now, what can be verified manually, and what risk remains uncovered.
- For `B`, `C`, and `D` work, state `预算与停止条件`: expected tool/turn budget, maximum corrective loops, and the point where work returns to `门下省`, `尚书省`, or the user instead of silently continuing.
- Use `best-minds` when expert framing materially improves strategy or research direction.
- Use `superpowers:writing-plans` when work needs a multi-step implementation plan.
- Identify which outputs are temporary case evidence and which are likely canonical updates.
- Keep output proportional to task size.

## Class Guidance

- `B`: produce a bounded province-only plan
- `C`: produce a full-chain plan with dispatch readiness
- `D`: split planning into `文线` and `武线` before review
  - `文线` defines research, comparison, and expert-framing work
  - `武线` defines prototype, feasibility, or engineering-probe work
  - the plan must define how the two tracks merge before final review

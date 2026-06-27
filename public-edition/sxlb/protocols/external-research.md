# 采风 Protocol

## Purpose

Define lightweight external research for `sxlb` planning cases.

`采风` is an external-evidence gathering protocol, not a new department（不是新部门）. It produces an `外部证据包` for `中书省` to use in planning, comparison, and decision-tree updates. It does not replace `中书省`, does not bypass `门下省`, and 不替中书省拍板.

## When To Use

Use `采风` only when a governed task materially depends on current or external information, such as:

- project planning that needs market, product, policy, library, or standards context
- comparing external repositories, tools, workflows, papers, or official docs
- deciding whether an outside practice should become a reference pattern
- validating claims that could be stale, promotional, or source-sensitive

Do not use it for ordinary local edits, clear implementation tasks, or questions already answerable from local source-of-truth files.

## Office Ownership

- `中书省` owns the research question tree and consumes the final `外部证据包`.
- `尚书省` may dispatch research slices when multiple independent evidence branches exist.
- `吏部` handles external skill, agent workflow, and capability-pattern scouting.
- `工部` handles external repo or technical feasibility evidence.
- `刑部` reviews source reliability, safety, license, security, and high-risk claims.
- `户部` handles data, pricing, metrics, market-size, and table-based evidence.
- `礼部` may turn the evidence package into user-facing explanation after review.

## Lightweight Bounds

Default bounds keep `采风` small:

- 2-5 subquestions
- 2-4 high-quality sources per subquestion
- prefer primary sources before commentary
- stop when evidence is enough to update the decision tree, not when the web is exhausted

If the task needs broader research, `中书省` should explicitly state why and ask `尚书省` to split the work.

## Source Types

Each source in the `外部证据包` must be labeled with one or more source types:

- `official`: official docs, standards, product pages, laws, or primary announcements
- `repo`: source repository, release notes, issues, pull requests, or commit history
- `paper`: paper, preprint, technical report, standard, or formal benchmark
- `data`: dataset, price table, financial/statistical source, or raw measurement
- `article`: tutorial, blog post, article, or news analysis
- `opinion`: forum, social media, anecdote, ranking, or subjective recommendation

Prefer `official`, `repo`, `paper`, and `data` for decisions. Treat `article` and `opinion` as context unless corroborated.

## External Evidence Package

A concise `外部证据包` must include:

- 调研问题：the question tree from `中书省`
- 子题拆分：2-5 scoped subquestions
- 来源清单：links or local source references
- 来源类型：one or more of `official`, `repo`, `paper`, `data`, `article`, or `opinion`
- 检查日期：date checked
- 来源可靠性：primary, corroborated, weak, promotional, stale, or other explicit reliability judgment
- 可用结论：what each source supports
- 不确定性：stale, weak, promotional, contradictory, or missing evidence
- 决策影响：how the evidence changes the plan, decision tree, or dispatch
- 复核请求：claims that need `刑部`, `工部`, `户部`, or `吏部` review

The package should be short enough for `中书省` to synthesize and specific enough for `门下省` to review.

## Review Rules

`门下省` should check:

- whether the evidence answers the question tree rather than collecting loose links
- whether source type and 来源可靠性 are visible
- whether current, high-stakes, or unstable claims have primary-source support
- whether weak sources are marked as weak instead of treated as settled
- whether the package clearly says what remains unknown

When source quality is insufficient, return `补证后再审` rather than letting `中书省` build a plan on loose material.

## Boundaries

- `采风` is a reference and evidence workflow, not an allowlist expansion.
- `采风` does not install external skills or import external projects by itself.
- `采风` does not turn a source into canonical truth without ordinary records routing and review.
- `采风` does not replace current restart-note or local source-of-truth routing.

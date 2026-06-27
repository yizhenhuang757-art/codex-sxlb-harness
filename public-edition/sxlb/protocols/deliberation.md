# Deliberation Protocol

## Purpose

Define how `会审` opens a structured full-court deliberation without breaking the main `sxlb` lifecycle.

## Trigger

- primary trigger: explicit user command `会审`
- exceptional trigger: `门下省` or `尚书省` may request `会审` when ordinary review would hide materially important disagreement

## When to Use

- the user wants to hear multiple offices argue the current plan
- the main dispute is strategic, not merely factual
- tradeoffs across scope, execution, verification, documentation, or automation need to be surfaced side by side
- `门下省` believes a single verdict would hide meaningful disagreement

## Host State

- `会审` runs inside visible `门下审议`
- it does not create a new top-level state
- it is a temporary deliberation sub-protocol rather than a persistent thread condition

## Required Participants

- `太子`
- `中书省`
- `门下省`
- `尚书省`
- relevant `六部`

Only summon the departments that actually bear on the dispute. Do not force every office to speak when they have no material angle.

## Required Outputs

- one `会审录`
- one post-deliberation disposition:
  - updated `中书方案`
  - updated `审议单`
  - updated `派令`
  - or direct `回奏` recommendation when no further execution is needed
- one explicit closing sentence from `太子`
- one explicit sentence stating that `会审` has ended and ordinary `sxlb` flow has resumed

## Deliberation Shape

1. `太子` states the disputed question
2. `中书省` gives the current plan and its rationale
3. `门下省` states the review concern
4. `尚书省` states the execution or dispatch consequence
5. each relevant department gives one office opinion
6. a first rebuttal round occurs across materially opposed offices
7. a second rebuttal round occurs by default when disagreement still matters after round one
8. any third rebuttal round requires explicit approval from `门下省`
9. `太子` closes with a tradeoff summary and recommended path
10. the transcript explicitly states that `会审` is closed and returns to the ordinary `sxlb` route

## Debate Rules

- every office must argue from its constitutional role
- each office should state:
  - position
  - strongest reason
  - strongest objection to the current route
  - what evidence would change its mind
- keep to one primary opinion per office unless the user explicitly asks for variants
- rebuttal defaults to two rounds
- a third round is exceptional and requires `门下省` to state why extra debate is still decision-useful
- beyond three rounds, `门下省` should normally cut off debate and route to `补证后再审` or summary judgment
- `门下省` may cut off circular debate and force summary

## Output Standard

`太子` must end with a concise summary covering:

- principal options
- main gains of each option
- main costs or risks of each option
- which option is recommended
- one backup option
- the cost of not adopting the recommended option
- whether the result requires re-plan, re-review, re-dispatch, or direct memorialization
- an explicit sentence that closes the `会审` sub-protocol
- an explicit sentence that returns the thread to ordinary `sxlb` handling

`太子` must give a clear recommendation sentence rather than a neutral recap. The summary is incomplete if it does not say what should be adopted now.
The summary is also protocol-defective if it fails to visibly close `会审` and hand control back to the normal `sxlb` flow.

## Relation To Other Commands

- `重审` asks for renewed review
- `会审` asks for explicit multi-office argument inside review
- `召回 <某部>` or `并行 <某部> <某部>` changes dispatch after review

Use `会审` when the user wants the disagreement surfaced, not hidden behind one summarized verdict.

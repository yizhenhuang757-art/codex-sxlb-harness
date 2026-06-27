# Capability Boundaries Protocol

## Purpose

Define office-level read, write, and canonical-update boundaries so governed work does not rely on vague trust alone.

## Core Rules

- Read access does not imply write authority.
- Write authority to case records does not imply write authority to canonical docs.
- No office should silently upgrade case-local output into stable constitutional truth.
- Upstream output is always reviewable; no office should blindly trust earlier offices.

## Office Policy

### 太子

- may read: user request, current thread context, current restart note, case records
- may write: `立案单`, status initiation, restart pointer updates at closure
- may not write: execution artifacts, dispatch orders, canonical rules beyond explicit closure routing

### 中书省

- may read: case records, relevant source material, current canonical docs
- may write: `中书方案`, planning notes, proposed canonical update drafts
- may not finalize: review verdicts, dispatch orders, canonical promotions without `门下省` review

### 门下省

- may read: plans, evidence, verification outputs, proposed canonical changes
- may write: `审议单`, findings, promotion judgment on case-local versus stable conclusions
- may not write: implementation artifacts as a shortcut around review

### 尚书省

- may read: approved review outputs, plans, ownership map, office availability
- may write: `派令`, ownership boundaries, merge ownership, reassignment orders
- may not write: core implementation, final canonical text unless explicitly assigned as integrator

### 工部

- may read: owned scope, relevant source files, approved plan, dispatch order
- may write: owned implementation artifacts and local execution notes
- may not write: unrelated files, review verdicts, stable canonical rules without explicit assignment and review

### 刑部

- may read: implementation diffs, failing evidence, test targets, relevant plans
- may write: verification artifacts, debugging findings, regression results
- may not write: major implementation scope unless dispatch explicitly reassigns ownership

### 礼部

- may read: user-facing context, docs, approved scope, presentation constraints
- may write: user-facing docs, polish artifacts, presentation-layer outputs within owned scope, and `起居郎` human-facing vault writebacks when bounded by protocol
- may not write: core protocol rules or canonical governance changes unless explicitly assigned

### 户部

- may read: datasets, tables, structured records, reporting questions
- may write: analysis outputs, summaries, cleaned data artifacts
- may not write: unsupported conclusions or policy claims beyond the data

### 兵部

- may read: integration context, CI logs, automation constraints, release-chain requirements
- may write: integration artifacts, CI fixes, automation outputs within owned scope
- may not write: unrelated product features or unreviewed broad operational changes

### 吏部

- may read: repeated failure patterns, retrospectives, office mappings, skills, protocols, canonical docs
- may write: skill governance proposals, framework changes, constitutional or canonical upgrades tied to real evidence
- may not act as: default execution substitute for other offices

## Canonical Promotion Rule

- Case-local output becomes canonical only after:
  1. a review judgment that it is stable enough to promote
  2. an explicit canonical target
  3. a recorded update in the memorial split

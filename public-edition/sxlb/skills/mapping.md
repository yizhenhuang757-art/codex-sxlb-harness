# Skill Mapping

## Purpose

Define how the 三省六部制 SXLB Codex framework maps offices to the local skill library.

## Mapping Principles

- Province offices own process discipline.
- Department offices own specialized execution.
- `尚书省` may name task-specific canonical skills in a dispatch order only if they are already legal under the office allowlist.
- `吏部` governs capability growth instead of acting as a default execution office.
- Host-required process skills stay in force for every office and are not overridden by office mapping.
- External skill projects may contribute `参考模式` only after `吏部` capability judgment; a reference pattern is vocabulary or checklist guidance, not a callable skill and not a change to any office allowlist.

## Precedence Rules

- `allowlist.md` defines which skill families or canonical skills an office may use at all.
- `skill-families.md` defines the daily family routing surface.
- `skill-inventory.generated.md` records concrete `SKILL.md` files for audit and expansion.
- `mapping.md` defines how those allowed skills should be used.
- `primary` means default choice for that office.
- `support` means conditional use inside the office's normal role boundary.
- `task-specific extensions` require an explicit dispatch need.
- `retrospection` applies only after or between governed task runs.
- capability-boundary rules stay in force even when a skill is allowlisted.

## Province Mapping

### 太子

- primary:
  - `superpowers:brainstorming` for intake clarification: open the problem space enough to classify the case, name constraints, and choose the next office.
- support:
  - `planning-with-files` for persistent worklog support only
  - When the user explicitly asks for `planning-with-files` during an active `sxlb` case, treat that request as `太子` invoking the skill unless the user clearly assigns it elsewhere.

### 中书省

- primary:
  - `superpowers:brainstorming` for plan shaping: compare possible routes, surface tradeoffs, and turn the filed case into plan options.
  - `superpowers:writing-plans`
  - `best-minds`
- support:
  - `workflow-orchestration-patterns`
  - agent-side family recall during planning, especially when the task resembles design/prototype work, browser execution, documents, slides, spreadsheets, email, citations, security review, GitHub/CI, or creative production

### 门下省

- primary:
  - `superpowers:verification-before-completion`
  - `superpowers:requesting-code-review`
  - `superpowers:receiving-code-review`
- support:
  - `superpowers:systematic-debugging` only when reviewing whether evidence is sufficient, not for taking over debugging

### 尚书省

- primary:
  - `superpowers:subagent-driven-development`
  - `superpowers:dispatching-parallel-agents`
  - `superpowers:using-git-worktrees`
- support:
  - `sxlb-agent-dispatch-check` before turning a dispatch into real subagent execution, parallel agents, or OMX-style execution

## Department Mapping

### 工部

- primary:
  - `superpowers:test-driven-development`
  - `workflow-orchestration-patterns`
  - `plugin-creator`
- task-specific extensions:
  - `family:plugin/browser` for localhost, file URL, screenshot, click/type, and visual smoke-test loops
  - `family:plugin/product-design` for implementing a selected screenshot, mockup, generated product-design reference, or live URL prototype
  - `family:documents-media-data` for code-adjacent document/media/data artifacts when explicitly dispatched

### 刑部

- primary:
  - `superpowers:systematic-debugging`
  - `superpowers:verification-before-completion`
  - `superpowers:requesting-code-review`
- support:
  - `family:plugin/browser` for local UI verification and screenshot evidence
  - `family:plugin/codex-security` for repository security scans, diff scans, attack-path analysis, finding discovery, validation, and fixing validated or plausible security findings

### 礼部

- primary:
  - `frontend-design`
  - `docx`
  - `pptx`
  - `obsidian-markdown`
  - `humanizer-zh`
- support:
  - `family:plugin/figma` for Figma URLs, design-system work, mockups, diagrams, FigJam, Slides, and design handoff
  - `family:plugin/product-design` for product direction, prototype exploration, UX audits, design QA, user context, live-URL prototyping, screenshot-to-code, and sharing reviewable prototypes
  - `family:plugin/presentations`, `family:plugin/documents`, `family:plugin/canva`, and `family:plugin/creative-production` for user-facing decks, docs, Canva designs, campaign visuals, and creative exploration
  - `family:toefl` for TOEFL item review, speaking scoring, writing sentence-building, and study-loop note work when the deliverable is learner-facing feedback or prose quality
- standing officer:
  - `起居郎` uses `humanizer-zh` for Chinese human-facing vault text when final polish or AI-trace cleanup is needed, without changing factual conclusions.

### 户部

- primary:
  - `spreadsheet`
  - `csv-data-summarizer`
  - `ticktick-analytics`
- support:
  - `family:plugin/spreadsheets` for workbook creation, spreadsheet analysis, charts, and Google Sheets-ready outputs
  - `family:plugin/zotero` for 文献库 search, metadata inventory, BibTeX export, citation insertion, indexed full-text retrieval when requested, and 引用数据 preparation for reading, research, and writing workflows
  - `family:reading-research` for Reading Lab notes, Zotero thinking sync, NotebookLM queries, and chapter workbench evidence organization
  - `family:toefl` for TOEFL evidence tracking, daily-loop accounting, review cadence, and study-progress surfaces
  - Zotero library writes, imports, or saves require explicit confirmation before execution.

### 兵部

- primary:
  - `github:github`
  - `github:gh-fix-ci`
  - `github:gh-address-comments`
  - `github:yeet`
  - `workflow-orchestration-patterns`
- support:
  - `family:plugin/chrome` for真实 Chrome 登录态 browser execution, 已打开标签页 handoff, authenticated web workflows, 网页表单 filling, file-upload flows, and external-service operations assigned by `尚书省`
  - `family:plugin/computer-use` for local Mac app UI control when no dedicated plugin, connector, structured API, Browser, or Chrome route can complete the task
  - `family:plugin/github` for repository, pull request, issue, CI, and publishing tasks when they are integration or release-chain work
  - `family:plugin/outlook-email` for mail triage, reply drafting, task extraction, and shared mailbox workflows when the task is operational coordination rather than prose-only writing
  - Use Chrome DevTools or `chrome-devtools` for console, network, performance, Lighthouse, and DOM-level diagnosis; `chrome:Chrome` should不要替代 Chrome DevTools 的诊断职责.

### 吏部

- primary:
  - `superpowers:writing-skills`
  - `skill-creator`
  - `find-skills`
- support:
  - `sxlb-agent-dispatch-check` when maintaining or revising the real-subagent dispatch gate
  - OpenAI 插件 capability review and 插件能力晋升 decisions when a plugin materially changes an office's execution surface
- retrospection:
  - `self-improving-agent`

## Governance Rules

- `find-skills` is owned by `吏部` and used when a real workflow gap appears.
- `find-skills` should normally produce a capability-scouting judgment with office owner, workflow gap, local-fit reasoning, and `可用 / 需用 / 急用` classification.
- Installed OpenAI 插件 may be allowlisted directly only after `吏部` ties them to a repeated or high-value workflow need and classifies their office fit as `可用 / 需用 / 急用`.
- External skills discovered by `吏部` may remain reference patterns rather than installed framework dependencies when local adoption is not yet justified.
- Reference patterns may shape planning, dispatch, review, or verification language, but they must not trigger skill loading, bypass office ownership, or expand write authority.
- `self-improving-agent` is triggered by `吏部` after failed runs, repeated rework, or framework-level friction.
- No office may call a skill outside its allowlist unless `吏部` formally updates the framework.
- Family allowlist entries may expand only to concrete skills recorded in `skill-inventory.generated.md`.
- Nested vendor skills marked `reference-only` are not callable through family expansion.
- `family:plugin/computer-use` is a fallback for local GUI operation, not a first-choice automation layer; risky direct UI actions follow the Computer Use confirmation policy.
- Skill legality does not override office write boundaries or canonical-promotion rules.

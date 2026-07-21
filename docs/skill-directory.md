---
layout: default
title: Office and skill directory
lang: en
alternate: /zh-CN/skill-directory/
directory_filter: true
description: Search the SXLB public skill directory by office, lifecycle, and source relationship.
---

# Office and skill directory

This directory lists every skill record in the public inventory. The source relation states whether SXLB bundles it, a host supplies it, or a verified external reference exists. Entries without a public upstream URL say so directly.

<label class="directory-filter-label" for="directory-filter">Filter directory</label>
<input id="directory-filter" data-directory-filter type="search" placeholder="Type an office, skill, or source">
<p id="directory-count" aria-live="polite"></p>

| Office | Skill | Lifecycle | Delivery | Source relationship | Use note |
| --- | --- | --- | --- | --- | --- |
| host / 三省 | `superpowers:brainstorming` | active | optional-interface | Host interface: Optional interface supplied by a host environment; the public inventory does not declare an upstream URL. | optional host workflow skill; not bundled |
| host / 三省 | `superpowers:dispatching-parallel-agents` | active | optional-interface | Host interface: Optional interface supplied by a host environment; the public inventory does not declare an upstream URL. | optional host workflow skill; not bundled |
| host / 三省 | `superpowers:executing-plans` | active | optional-interface | Host interface: Optional interface supplied by a host environment; the public inventory does not declare an upstream URL. | optional host workflow skill; not bundled |
| host / 三省 | `superpowers:finishing-a-development-branch` | active | optional-interface | Host interface: Optional interface supplied by a host environment; the public inventory does not declare an upstream URL. | optional host workflow skill; not bundled |
| host / 三省 | `superpowers:receiving-code-review` | active | optional-interface | Host interface: Optional interface supplied by a host environment; the public inventory does not declare an upstream URL. | optional host workflow skill; not bundled |
| host / 三省 | `superpowers:requesting-code-review` | active | optional-interface | Host interface: Optional interface supplied by a host environment; the public inventory does not declare an upstream URL. | optional host workflow skill; not bundled |
| host / 三省 | `superpowers:subagent-driven-development` | active | optional-interface | Host interface: Optional interface supplied by a host environment; the public inventory does not declare an upstream URL. | optional host workflow skill; not bundled |
| host / 三省 | `superpowers:systematic-debugging` | active | optional-interface | Host interface: Optional interface supplied by a host environment; the public inventory does not declare an upstream URL. | optional host workflow skill; not bundled |
| host / 三省 | `superpowers:test-driven-development` | active | optional-interface | Host interface: Optional interface supplied by a host environment; the public inventory does not declare an upstream URL. | optional host workflow skill; not bundled |
| host / 三省 | `superpowers:using-git-worktrees` | active | optional-interface | Host interface: Optional interface supplied by a host environment; the public inventory does not declare an upstream URL. | optional host workflow skill; not bundled |
| host / 三省 | `superpowers:using-superpowers` | active | optional-interface | Host interface: Optional interface supplied by a host environment; the public inventory does not declare an upstream URL. | optional host workflow skill; not bundled |
| host / 三省 | `superpowers:verification-before-completion` | active | optional-interface | Host interface: Optional interface supplied by a host environment; the public inventory does not declare an upstream URL. | optional host workflow skill; not bundled |
| host / 三省 | `superpowers:writing-plans` | active | optional-interface | Host interface: Optional interface supplied by a host environment; the public inventory does not declare an upstream URL. | optional host workflow skill; not bundled |
| host / 三省 | `superpowers:writing-skills` | active | optional-interface | Host interface: Optional interface supplied by a host environment; the public inventory does not declare an upstream URL. | optional host workflow skill; not bundled |
| 中书省 | `best-minds` | active | optional-interface | Host interface: Optional interface supplied by a host environment; the public inventory does not declare an upstream URL. | optional expert-framing interface |
| 兵部 | `agent-reach` | active | optional-interface | External reference: [Agent-Reach](https://github.com/Panniantong/Agent-Reach) | optional public research and platform routing interface |
| 兵部 | `chrome:control-chrome` | active-via-family | plugin-cache | Plugin family: Supplied by an installed host plugin family; no upstream URL is declared in the public inventory. | concrete plugin skill; route through plugin family |
| 兵部 | `workflow-orchestration-patterns` | active | optional-interface | Host interface: Optional interface supplied by a host environment; the public inventory does not declare an upstream URL. | optional workflow design interface |
| 兵部 / 刑部 / 门下省 | `computer-use:computer-use` | active-via-family | plugin-cache | Plugin family: Supplied by an installed host plugin family; no upstream URL is declared in the public inventory. | concrete plugin skill; route through plugin family |
| 兵部 / 礼部 | `outlook-email:outlook-email` | active-via-family | plugin-cache | Plugin family: Supplied by an installed host plugin family; no upstream URL is declared in the public inventory. | concrete plugin skill; route through plugin family |
| 刑部 | `codex-security:deep-security-scan` | active-via-family | plugin-cache | Plugin family: Supplied by an installed host plugin family; no upstream URL is declared in the public inventory. | concrete plugin skill; route through plugin family |
| 刑部 | `codex-security:security-scan` | active-via-family | plugin-cache | Plugin family: Supplied by an installed host plugin family; no upstream URL is declared in the public inventory. | concrete plugin skill; route through plugin family |
| 吏部 | `find-skills` | active | optional-interface | Host interface: Optional interface supplied by a host environment; the public inventory does not declare an upstream URL. | optional skill discovery interface |
| 吏部 | `plugin-creator` | active | optional-interface | Host interface: Optional interface supplied by a host environment; the public inventory does not declare an upstream URL. | optional plugin creation interface |
| 吏部 | `self-improving-agent` | active | optional-interface | Host interface: Optional interface supplied by a host environment; the public inventory does not declare an upstream URL. | optional retrospection interface |
| 吏部 | `skill-onboarding` | active | optional-interface | Host interface: Optional interface supplied by a host environment; the public inventory does not declare an upstream URL. | optional new-skill onboarding interface |
| 吏部 / 太子 | `guoshiguan-recall` | active | optional-interface | Host interface: Optional interface supplied by a host environment; the public inventory does not declare an upstream URL. | optional interface; private case history is not bundled |
| 吏部 / 太子 | `memory-gateway` | active | optional-interface | Host interface: Optional interface supplied by a host environment; the public inventory does not declare an upstream URL. | optional interface; private memory stores are not bundled |
| 吏部 / 太子 | `planning-with-files` | active | optional-interface | Host interface: Optional interface supplied by a host environment; the public inventory does not declare an upstream URL. | optional interface; private implementations are not bundled |
| 吏部 / 太子 | `sxlb` | active | public-bundle | Public bundle: Bundled and maintained in this public repository. | public bundled harness skill |
| 吏部 / 太子 | `sxlb-agent-dispatch-check` | active | public-bundle | Public bundle: Bundled companion skill maintained in this public repository. | optional companion dispatch gate |
| 工部 / 刑部 | `browser:control-in-app-browser` | active-via-family | plugin-cache | Plugin family: Supplied by an installed host plugin family; no upstream URL is declared in the public inventory. | concrete plugin skill; route through plugin family |
| 户部 | `notebooklm` | active | optional-interface | Host interface: Optional interface supplied by a host environment; the public inventory does not declare an upstream URL. | optional research interface |
| 户部 | `spreadsheets:Spreadsheets` | active-via-family | plugin-cache | Plugin family: Supplied by an installed host plugin family; no upstream URL is declared in the public inventory. | concrete plugin skill; route through plugin family |
| 户部 | `zotero-chapter-workbench` | active | optional-interface | Host interface: Optional interface supplied by a host environment; the public inventory does not declare an upstream URL. | optional citation workflow interface |
| 户部 | `zotero:Zotero` | active-via-family | plugin-cache | Plugin family: Supplied by an installed host plugin family; no upstream URL is declared in the public inventory. | concrete plugin skill; route through plugin family |
| 礼部 | `figma:figma-generate-diagram` | active-via-family | plugin-cache | Plugin family: Supplied by an installed host plugin family; no upstream URL is declared in the public inventory. | concrete plugin skill; route through plugin family |
| 礼部 | `figma:figma-use` | active-via-family | plugin-cache | Plugin family: Supplied by an installed host plugin family; no upstream URL is declared in the public inventory. | concrete plugin skill; route through plugin family |
| 礼部 | `humanizer-zh` | active | optional-interface | External reference: [Humanizer-zh](https://github.com/op7418/Humanizer-zh) | optional writing polish interface |
| 礼部 | `presentations:Presentations` | active-via-family | plugin-cache | Plugin family: Supplied by an installed host plugin family; no upstream URL is declared in the public inventory. | concrete plugin skill; route through plugin family |
| 礼部 / 工部 | `frontend-design` | active | optional-interface | Host interface: Optional interface supplied by a host environment; the public inventory does not declare an upstream URL. | optional frontend design interface |
| 礼部 / 工部 | `product-design:design-qa` | active-via-family | plugin-cache | Plugin family: Supplied by an installed host plugin family; no upstream URL is declared in the public inventory. | concrete plugin skill; route through plugin family |
| 礼部 / 工部 | `product-design:get-context` | active-via-family | plugin-cache | Plugin family: Supplied by an installed host plugin family; no upstream URL is declared in the public inventory. | concrete plugin skill; route through plugin family |
| 礼部 / 工部 | `product-design:image-to-code` | active-via-family | plugin-cache | Plugin family: Supplied by an installed host plugin family; no upstream URL is declared in the public inventory. | concrete plugin skill; route through plugin family |
| 礼部 / 工部 | `product-design:prototype` | active-via-family | plugin-cache | Plugin family: Supplied by an installed host plugin family; no upstream URL is declared in the public inventory. | concrete plugin skill; route through plugin family |
| 礼部 / 工部 | `product-design:url-to-code` | active-via-family | plugin-cache | Plugin family: Supplied by an installed host plugin family; no upstream URL is declared in the public inventory. | concrete plugin skill; route through plugin family |
| 礼部 / 户部 | `docx` | active | optional-interface | Host interface: Optional interface supplied by a host environment; the public inventory does not declare an upstream URL. | optional document artifact interface |
| 礼部 / 户部 | `pdf:pdf` | active-via-family | plugin-cache | Plugin family: Supplied by an installed host plugin family; no upstream URL is declared in the public inventory. | concrete plugin skill; route through plugin family |
| 礼部 / 户部 | `toefl-reading-review` | active | optional-interface | Host interface: Optional interface supplied by a host environment; the public inventory does not declare an upstream URL. | optional learning workflow interface |

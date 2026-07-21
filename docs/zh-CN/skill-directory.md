---
layout: default
title: 部门与技能目录
lang: zh-CN
alternate: /skill-directory/
directory_filter: true
description: 按部门、生命周期和来源关系检索 SXLB 公共版技能目录。
---

# 部门与技能目录

目录列出公共清单中的全部技能记录。来源关系说明该技能是否随公共包交付、由宿主环境提供，或有可验证的外部参考。没有公开来源链接的条目会直接说明这一点。

<label class="directory-filter-label" for="directory-filter">筛选目录</label>
<input id="directory-filter" data-directory-filter type="search" placeholder="输入部门、技能或来源">
<p id="directory-count" aria-live="polite"></p>

| 部门 | 技能 | 生命周期 | 交付状态 | 来源关系 | 使用说明 |
| --- | --- | --- | --- | --- | --- |
| host / 三省 | `superpowers:brainstorming` | active | optional-interface | 宿主接口: Optional interface supplied by a host environment; the public inventory does not declare an upstream URL. | optional host workflow skill; not bundled |
| host / 三省 | `superpowers:dispatching-parallel-agents` | active | optional-interface | 宿主接口: Optional interface supplied by a host environment; the public inventory does not declare an upstream URL. | optional host workflow skill; not bundled |
| host / 三省 | `superpowers:executing-plans` | active | optional-interface | 宿主接口: Optional interface supplied by a host environment; the public inventory does not declare an upstream URL. | optional host workflow skill; not bundled |
| host / 三省 | `superpowers:finishing-a-development-branch` | active | optional-interface | 宿主接口: Optional interface supplied by a host environment; the public inventory does not declare an upstream URL. | optional host workflow skill; not bundled |
| host / 三省 | `superpowers:receiving-code-review` | active | optional-interface | 宿主接口: Optional interface supplied by a host environment; the public inventory does not declare an upstream URL. | optional host workflow skill; not bundled |
| host / 三省 | `superpowers:requesting-code-review` | active | optional-interface | 宿主接口: Optional interface supplied by a host environment; the public inventory does not declare an upstream URL. | optional host workflow skill; not bundled |
| host / 三省 | `superpowers:subagent-driven-development` | active | optional-interface | 宿主接口: Optional interface supplied by a host environment; the public inventory does not declare an upstream URL. | optional host workflow skill; not bundled |
| host / 三省 | `superpowers:systematic-debugging` | active | optional-interface | 宿主接口: Optional interface supplied by a host environment; the public inventory does not declare an upstream URL. | optional host workflow skill; not bundled |
| host / 三省 | `superpowers:test-driven-development` | active | optional-interface | 宿主接口: Optional interface supplied by a host environment; the public inventory does not declare an upstream URL. | optional host workflow skill; not bundled |
| host / 三省 | `superpowers:using-git-worktrees` | active | optional-interface | 宿主接口: Optional interface supplied by a host environment; the public inventory does not declare an upstream URL. | optional host workflow skill; not bundled |
| host / 三省 | `superpowers:using-superpowers` | active | optional-interface | 宿主接口: Optional interface supplied by a host environment; the public inventory does not declare an upstream URL. | optional host workflow skill; not bundled |
| host / 三省 | `superpowers:verification-before-completion` | active | optional-interface | 宿主接口: Optional interface supplied by a host environment; the public inventory does not declare an upstream URL. | optional host workflow skill; not bundled |
| host / 三省 | `superpowers:writing-plans` | active | optional-interface | 宿主接口: Optional interface supplied by a host environment; the public inventory does not declare an upstream URL. | optional host workflow skill; not bundled |
| host / 三省 | `superpowers:writing-skills` | active | optional-interface | 宿主接口: Optional interface supplied by a host environment; the public inventory does not declare an upstream URL. | optional host workflow skill; not bundled |
| 中书省 | `best-minds` | active | optional-interface | 宿主接口: Optional interface supplied by a host environment; the public inventory does not declare an upstream URL. | optional expert-framing interface |
| 兵部 | `agent-reach` | active | optional-interface | 外部参考: [Agent-Reach](https://github.com/Panniantong/Agent-Reach) | optional public research and platform routing interface |
| 兵部 | `chrome:control-chrome` | active-via-family | plugin-cache | 插件能力族: Supplied by an installed host plugin family; no upstream URL is declared in the public inventory. | concrete plugin skill; route through plugin family |
| 兵部 | `workflow-orchestration-patterns` | active | optional-interface | 宿主接口: Optional interface supplied by a host environment; the public inventory does not declare an upstream URL. | optional workflow design interface |
| 兵部 / 刑部 / 门下省 | `computer-use:computer-use` | active-via-family | plugin-cache | 插件能力族: Supplied by an installed host plugin family; no upstream URL is declared in the public inventory. | concrete plugin skill; route through plugin family |
| 兵部 / 礼部 | `outlook-email:outlook-email` | active-via-family | plugin-cache | 插件能力族: Supplied by an installed host plugin family; no upstream URL is declared in the public inventory. | concrete plugin skill; route through plugin family |
| 刑部 | `codex-security:deep-security-scan` | active-via-family | plugin-cache | 插件能力族: Supplied by an installed host plugin family; no upstream URL is declared in the public inventory. | concrete plugin skill; route through plugin family |
| 刑部 | `codex-security:security-scan` | active-via-family | plugin-cache | 插件能力族: Supplied by an installed host plugin family; no upstream URL is declared in the public inventory. | concrete plugin skill; route through plugin family |
| 吏部 | `find-skills` | active | optional-interface | 宿主接口: Optional interface supplied by a host environment; the public inventory does not declare an upstream URL. | optional skill discovery interface |
| 吏部 | `plugin-creator` | active | optional-interface | 宿主接口: Optional interface supplied by a host environment; the public inventory does not declare an upstream URL. | optional plugin creation interface |
| 吏部 | `self-improving-agent` | active | optional-interface | 宿主接口: Optional interface supplied by a host environment; the public inventory does not declare an upstream URL. | optional retrospection interface |
| 吏部 | `skill-onboarding` | active | optional-interface | 宿主接口: Optional interface supplied by a host environment; the public inventory does not declare an upstream URL. | optional new-skill onboarding interface |
| 吏部 / 太子 | `guoshiguan-recall` | active | optional-interface | 宿主接口: Optional interface supplied by a host environment; the public inventory does not declare an upstream URL. | optional interface; private case history is not bundled |
| 吏部 / 太子 | `memory-gateway` | active | optional-interface | 宿主接口: Optional interface supplied by a host environment; the public inventory does not declare an upstream URL. | optional interface; private memory stores are not bundled |
| 吏部 / 太子 | `planning-with-files` | active | optional-interface | 宿主接口: Optional interface supplied by a host environment; the public inventory does not declare an upstream URL. | optional interface; private implementations are not bundled |
| 吏部 / 太子 | `sxlb` | active | public-bundle | 公共包: Bundled and maintained in this public repository. | public bundled harness skill |
| 吏部 / 太子 | `sxlb-agent-dispatch-check` | active | public-bundle | 公共包: Bundled companion skill maintained in this public repository. | optional companion dispatch gate |
| 工部 / 刑部 | `browser:control-in-app-browser` | active-via-family | plugin-cache | 插件能力族: Supplied by an installed host plugin family; no upstream URL is declared in the public inventory. | concrete plugin skill; route through plugin family |
| 户部 | `notebooklm` | active | optional-interface | 宿主接口: Optional interface supplied by a host environment; the public inventory does not declare an upstream URL. | optional research interface |
| 户部 | `spreadsheets:Spreadsheets` | active-via-family | plugin-cache | 插件能力族: Supplied by an installed host plugin family; no upstream URL is declared in the public inventory. | concrete plugin skill; route through plugin family |
| 户部 | `zotero-chapter-workbench` | active | optional-interface | 宿主接口: Optional interface supplied by a host environment; the public inventory does not declare an upstream URL. | optional citation workflow interface |
| 户部 | `zotero:Zotero` | active-via-family | plugin-cache | 插件能力族: Supplied by an installed host plugin family; no upstream URL is declared in the public inventory. | concrete plugin skill; route through plugin family |
| 礼部 | `figma:figma-generate-diagram` | active-via-family | plugin-cache | 插件能力族: Supplied by an installed host plugin family; no upstream URL is declared in the public inventory. | concrete plugin skill; route through plugin family |
| 礼部 | `figma:figma-use` | active-via-family | plugin-cache | 插件能力族: Supplied by an installed host plugin family; no upstream URL is declared in the public inventory. | concrete plugin skill; route through plugin family |
| 礼部 | `humanizer-zh` | active | optional-interface | 外部参考: [Humanizer-zh](https://github.com/op7418/Humanizer-zh) | optional writing polish interface |
| 礼部 | `presentations:Presentations` | active-via-family | plugin-cache | 插件能力族: Supplied by an installed host plugin family; no upstream URL is declared in the public inventory. | concrete plugin skill; route through plugin family |
| 礼部 / 工部 | `frontend-design` | active | optional-interface | 宿主接口: Optional interface supplied by a host environment; the public inventory does not declare an upstream URL. | optional frontend design interface |
| 礼部 / 工部 | `product-design:design-qa` | active-via-family | plugin-cache | 插件能力族: Supplied by an installed host plugin family; no upstream URL is declared in the public inventory. | concrete plugin skill; route through plugin family |
| 礼部 / 工部 | `product-design:get-context` | active-via-family | plugin-cache | 插件能力族: Supplied by an installed host plugin family; no upstream URL is declared in the public inventory. | concrete plugin skill; route through plugin family |
| 礼部 / 工部 | `product-design:image-to-code` | active-via-family | plugin-cache | 插件能力族: Supplied by an installed host plugin family; no upstream URL is declared in the public inventory. | concrete plugin skill; route through plugin family |
| 礼部 / 工部 | `product-design:prototype` | active-via-family | plugin-cache | 插件能力族: Supplied by an installed host plugin family; no upstream URL is declared in the public inventory. | concrete plugin skill; route through plugin family |
| 礼部 / 工部 | `product-design:url-to-code` | active-via-family | plugin-cache | 插件能力族: Supplied by an installed host plugin family; no upstream URL is declared in the public inventory. | concrete plugin skill; route through plugin family |
| 礼部 / 户部 | `docx` | active | optional-interface | 宿主接口: Optional interface supplied by a host environment; the public inventory does not declare an upstream URL. | optional document artifact interface |
| 礼部 / 户部 | `pdf:pdf` | active-via-family | plugin-cache | 插件能力族: Supplied by an installed host plugin family; no upstream URL is declared in the public inventory. | concrete plugin skill; route through plugin family |
| 礼部 / 户部 | `toefl-reading-review` | active | optional-interface | 宿主接口: Optional interface supplied by a host environment; the public inventory does not declare an upstream URL. | optional learning workflow interface |

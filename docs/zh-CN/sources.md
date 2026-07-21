---
layout: default
title: 来源与关系说明
lang: zh-CN
alternate: /sources/
description: 说明 SXLB 的灵感来源、公共包、宿主接口与插件能力族。
---

# 来源与关系说明

本页区分灵感来源、随包代码、宿主接口和插件能力族。一个链接说明存在已记录的关系，不自动证明 SXLB 包含该项目的代码。

## 原始灵感

[cft0808/edict](https://github.com/cft0808/edict) 是 SXLB 使用三省六部来表达智能体分工时的主要灵感来源。其[任务派发架构](https://github.com/cft0808/edict/blob/main/docs/task-dispatch-architecture.md)为“已批准任务如何成为有边界的派发”提供了参考问题。

SXLB 是独立实现的 Codex 技能工具。它不内置、不 fork、也不复刻 Edict 或 OpenClaw 的源代码。

## 公共包

`sxlb` 工具和 `sxlb-agent-dispatch-check` 配套技能由本仓库维护。公共包在隐私审查后交付它们的协议、模板、脚本和测试。

## 可选接口与插件能力族

目录还列出可选的宿主技能和插件能力族。列出某个接口，只表示当宿主环境提供它、且负责部门允许时，SXLB 可以将兼容工作路由给它；这不表示 SXLB 随包交付该实现、认可其每个版本，或继承其许可证。

当公共清单没有声明上游链接时，目录会直接说明。这是有意的：缺少来源链接不等于可以猜测其出处。

打开[部门与技能目录]({{ '/zh-CN/skill-directory/' | relative_url }})，查看全部记录。

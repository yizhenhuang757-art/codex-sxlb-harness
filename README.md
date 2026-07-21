# SXLB / 三省六部治理工具

SXLB 是一套以文本为先的治理工具：它帮助个人或团队把工作组织为可检查的提案、复核、执行、验证与留痕链条。

SXLB 是面向 Codex 的独立实现，受到 [cft0808/edict](https://github.com/cft0808/edict) 及其[任务派发架构](https://github.com/cft0808/edict/blob/main/docs/task-dispatch-architecture.md)启发。它不内置、不 fork，也不复刻 Edict 或 OpenClaw 的代码。项目关系与设计差异见[为什么还有 SXLB](docs/zh-CN/why-sxlb.md)和[Why SXLB exists](docs/why-sxlb.md)。

## Start here / 从这里开始

- [English documentation](docs/index.md)
- [中文说明文档](docs/zh-CN/index.md)
- [Quick start](docs/quickstart.md) / [快速开始](docs/zh-CN/quickstart.md)
- [Outcomes and features](docs/features.md) / [效果与功能](docs/zh-CN/features.md)
- [Why SXLB exists](docs/why-sxlb.md) / [为什么还有 SXLB](docs/zh-CN/why-sxlb.md)
- [Office and skill directory](docs/skill-directory.md) / [部门与技能目录](docs/zh-CN/skill-directory.md)
- [Sources and relationships](docs/sources.md) / [来源与关系说明](docs/zh-CN/sources.md)

The documentation leads with installation and use. It then explains the workflow, the historical model of the Three Departments and Six Ministries, and the modern SXLB mapping.

文档将安装和使用放在最前面；之后依次介绍工作流、三省六部的历史模型，以及 SXLB 的现代映射。

## What is included / 包含内容

- The sanitized `sxlb` governance harness
- The `sxlb-agent-dispatch-check` companion skill
- Portable templates, scripts, tests, and public documentation
- No private worklogs, vault data, credentials, browser profiles, or personal skill inventory

## Public-edition boundary / 公共版边界

This repository publishes reusable protocols and empty, user-owned operating surfaces. It does not publish the maintainer's private history, data, or current experimental runtime.

本仓库发布可复用的协议和由使用者拥有的空白操作空间，不发布维护者的私有历史、数据或正在试用的运行时版本。

## License

[MIT](LICENSE)

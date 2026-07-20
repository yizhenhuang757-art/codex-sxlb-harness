---
layout: default
title: 安装与快速开始
lang: zh-CN
alternate: /quickstart/
description: 安装公共 SXLB 包，并运行第一个受治理的案卷。
---

# 安装与快速开始

本页帮助你安装公共包，并运行一个小型案卷。该公共包与维护者的私有工作环境刻意分离。

## 1. 复制随包技能

先设定 Codex 技能所在的位置，再复制治理工具及其配套技能：

```bash
mkdir -p "$CODEX_SKILLS_HOME"
cp -R public-edition/sxlb "$CODEX_SKILLS_HOME/sxlb"
cp -R public-edition/companion-skills/sxlb-agent-dispatch-check \
  "$CODEX_SKILLS_HOME/sxlb-agent-dispatch-check"
```

建议使用 Python 3.11 或更高版本。SXLB 不需要后台服务。

## 2. 创建自己的操作空间

下列位置由你自己拥有。它们从空白开始，不会导入任何私有项目历史。

```bash
export SXLB_HOME="$CODEX_SKILLS_HOME/sxlb"
export SXLB_CASE_ROOT="$HOME/sxlb-cases"
export SXLB_GUOSHIGUAN_INDEX="$SXLB_CASE_ROOT/guoshiguan/index.md"
export SXLB_REFERENCE_POOL="$HOME/sxlb-reference-pool"

mkdir -p "$SXLB_CASE_ROOT/guoshiguan"
mkdir -p "$SXLB_REFERENCE_POOL/omx/upstream" \
  "$SXLB_REFERENCE_POOL/omx/extracted" \
  "$SXLB_REFERENCE_POOL/omx/evaluations"
cp "$SXLB_HOME/templates/guoshiguan-index.md" "$SXLB_GUOSHIGUAN_INDEX"
cp "$SXLB_HOME/templates/hanlinyuan-manifest.md" "$SXLB_REFERENCE_POOL/README.md"
```

## 3. 启动第一个案卷

新开一个 Codex 对话，并明确输入：

```text
sxlb
```

从边界清晰的请求开始，例如一份简短研究札记、一次发布检查或一项文稿审阅。好的第一个案卷应有明确产出和较小的证据范围。

## 4. 接下来会发生什么

SXLB 会让案卷路径可见：请求、提案、复核、执行、验证和结案。它会记录当前状态，使你能够判断发生了什么、下一步由谁负责，以及是否仍有未通过的复核关口。

需要完整次序时，请阅读[工作流参考]({{ '/zh-CN/workflow-reference/' | relative_url }})；想判断哪些部分适合自己的工作时，请阅读[效果与功能]({{ '/zh-CN/features/' | relative_url }})。

> 如需由 Agent 协助安装，也可以将[配套技能安装提示词]({{ '/prompts/agent-install-companion-skills' | relative_url }})复制给 Agent。

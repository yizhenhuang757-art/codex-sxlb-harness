---
layout: default
title: Installation and quick start
lang: en
alternate: /zh-CN/quickstart/
description: Install the public SXLB package and run a first governed case.
---

# Installation and quick start

Use this page to install the public package and run one small case. The package is deliberately separate from the maintainer's private operating environment.

## 1. Copy the bundled skills

Set the location where your Codex skills live, then copy the harness and its companion skill:

```bash
mkdir -p "$CODEX_SKILLS_HOME"
cp -R public-edition/sxlb "$CODEX_SKILLS_HOME/sxlb"
cp -R public-edition/companion-skills/sxlb-agent-dispatch-check \
  "$CODEX_SKILLS_HOME/sxlb-agent-dispatch-check"
```

Python 3.11 or later is recommended. SXLB does not need a background service.

## 2. Create your own operating surfaces

These locations belong to you. They begin empty and do not import any private project history.

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

## 3. Start a first case

Open a new Codex thread and explicitly enter:

```text
sxlb
```

Start with a bounded request: for example, ask for a short research note, a release check, or a document review. A good first case has a clear outcome and a small evidence set.

## 4. What happens next

SXLB makes the route through the case visible: request, proposal, review, execution, verification, and closure. It records the current state so you can tell what happened, who is responsible for the next move, and whether a review gate is still open.

Use the [workflow reference]({{ '/workflow-reference/' | relative_url }}) when you need the full sequence. Read [outcomes and features]({{ '/features/' | relative_url }}) to decide which parts are useful for your work.

> For assisted setup, you can also copy the [companion-skill installation prompt]({{ '/prompts/agent-install-companion-skills' | relative_url }}) into an Agent.

---
layout: default
title: Sources and relationships
lang: en
alternate: /zh-CN/sources/
description: Public source notes for SXLB's inspiration, methods, bundles, interfaces, and plugin families.
---

# Sources and relationships

This page distinguishes inspiration, method references, bundled code, host interfaces, and plugin families. A link shows a documented relationship. It does not, by itself, show that SXLB contains that project's code.

## Original inspiration

[cft0808/edict](https://github.com/cft0808/edict) is the primary project that inspired SXLB's use of 三省六部 as a vocabulary for differentiated agent roles. Its [task dispatch architecture](https://github.com/cft0808/edict/blob/main/docs/task-dispatch-architecture.md) informed the question of how an approved task becomes a bounded assignment.

SXLB is an independent Codex skill harness. It does not vendor, fork, or reproduce Edict or OpenClaw source code.

## Editorial methods used for this revision

- [Humanizer-zh](https://github.com/op7418/Humanizer-zh) guided the Chinese editing pass.
- [blader/humanizer](https://github.com/blader/humanizer) guided the English editing pass.
- [stop-slop](https://github.com/hardikpandya/stop-slop) is cited by Humanizer-zh as a practical reference.

These projects informed editorial review. They do not provide SXLB runtime logic.

## Public bundle

The `sxlb` harness and `sxlb-agent-dispatch-check` are maintained in this repository. The public package includes their protocols, templates, scripts, and tests after privacy review.

## Optional interfaces and plugin families

The directory also lists optional host skills and plugin families. A listed interface means SXLB may route compatible work to it when the host provides it and the responsible office permits it. It does not mean that SXLB bundles the implementation, endorses every version, or inherits its license.

When the public inventory does not declare an upstream URL, the directory says so. That is deliberate: an absent source link is not an invitation to guess at provenance.

Open the [office and skill directory]({{ '/skill-directory/' | relative_url }}) to inspect every record.

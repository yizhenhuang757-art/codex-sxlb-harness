# Agent Prompt: Install SXLB And Companion Skills

Use this prompt after cloning or downloading this repository. It is meant for an installation agent running on the user's own machine.

## Copy-Paste Prompt

```text
You are setting up the public HYZ/codex-sxlb-harness package for this local Codex environment.

Goal:
- Install the bundled `sxlb` harness skill.
- Install the bundled `sxlb-agent-dispatch-check` companion skill.
- Discover and install any available public/authorized companion workflow skills that improve the harness, without copying private data or account state.

Hard boundaries:
- Do not read, copy, upload, or publish private vaults, worklogs, email, TickTick data, Zotero libraries, browser profiles, cookies, tokens, plugin caches, or local MCP configs.
- Do not assume optional external skills are bundled. Treat them as optional interfaces unless they are already installed or available from a public/authorized source.
- Ask before installing plugins/connectors that require login, account access, browser state, or external service authorization.
- If a skill cannot be installed safely, record it as "missing optional dependency" and continue with the bundled harness.

Repository root:
- If I did not provide a path, first locate the cloned `codex-sxlb-harness` repository.
- Use `public-edition/sxlb` and `public-edition/companion-skills/sxlb-agent-dispatch-check` as the bundled skill sources.

Install the bundled skills:
1. Locate `$CODEX_SKILLS_HOME`. If it is unset, use the platform's normal Codex skills directory or ask me for the target directory.
2. Copy `public-edition/sxlb` to `$CODEX_SKILLS_HOME/sxlb`.
3. Copy `public-edition/companion-skills/sxlb-agent-dispatch-check` to `$CODEX_SKILLS_HOME/sxlb-agent-dispatch-check`.
4. Confirm both `SKILL.md` files exist after copying.

Set up empty public operating surfaces:
1. Create a user-owned case root such as `$HOME/sxlb-cases`.
2. Create a user-owned reference pool such as `$HOME/sxlb-reference-pool`.
3. Copy `public-edition/sxlb/templates/guoshiguan-index.md` into the new case root as an empty `国史馆` index.
4. Copy `public-edition/sxlb/templates/hanlinyuan-manifest.md` into the reference pool as its README or manifest.
5. Do not import anyone else's private history.

Discover optional companion skills:
- Check whether these optional interfaces are already installed:
  - `best-minds`
  - `planning-with-files`
  - `memory-gateway`
  - `guoshiguan-recall`
  - `agent-reach`
  - `workflow-orchestration-patterns`
  - `superpowers:using-superpowers`
  - `superpowers:brainstorming`
  - `superpowers:writing-plans`
  - `superpowers:test-driven-development`
  - `superpowers:systematic-debugging`
  - `superpowers:verification-before-completion`
  - `superpowers:requesting-code-review`
  - `superpowers:receiving-code-review`
  - `superpowers:subagent-driven-development`
  - `superpowers:dispatching-parallel-agents`
  - `superpowers:using-git-worktrees`
  - `superpowers:executing-plans`
  - `superpowers:finishing-a-development-branch`
  - `superpowers:writing-skills`
- If this environment has an official skill installer, use it only for public/authorized sources.
- If no installer or source is available, do not fabricate the skill. Mark it as missing optional dependency.
- Personal-domain skills such as TOEFL, TickTick, private communication workflows, private wiki workflows, and local Zotero-library workflows are not required for the public harness. Install them only if I explicitly request them and provide safe sources.

Verify:
1. Run the public `sxlb` tests if Python is available:
   `PYTHONPATH="<repo>/public-edition/sxlb/scripts:<repo>/public-edition/sxlb/tests" python3 -m unittest discover -s "<repo>/public-edition/sxlb/tests"`
2. Scan the installed/public files for obvious private paths or account strings before reporting success.
3. Start a fresh Codex thread and enter `sxlb`.

Report back with:
- installed bundled skills
- optional companion skills found
- optional companion skills installed
- optional companion skills missing
- verification commands and results
- any steps that require my approval
```

## Expected Result

The bundled harness works without optional skills. Optional companion skills improve planning, verification, debugging, research, and dispatch behavior when the user's environment already has them or can install them from a public/authorized source.

The prompt deliberately does not install private personal workflows by default.

# Install Draft

This is a draft install page for the future public edition.

## Manual Install

After the sanitized package exists:

```bash
mkdir -p "$CODEX_SKILLS_HOME"
cp -R public-edition/sxlb "$CODEX_SKILLS_HOME/sxlb"
cp -R public-edition/companion-skills/sxlb-agent-dispatch-check "$CODEX_SKILLS_HOME/sxlb-agent-dispatch-check"
```

Then start a new Codex thread and explicitly enter:

```text
sxlb
```

## Agent-Assisted Install

For a less manual setup, copy `docs/prompts/agent-install-companion-skills.md` into the Agent that will perform the installation.

That prompt tells the Agent to:

- install the bundled `sxlb` skill;
- install the bundled `sxlb-agent-dispatch-check` companion skill;
- create empty user-owned `国史馆` and `翰林院` operating surfaces;
- discover optional public/authorized companion workflow skills such as `best-minds` and `superpowers:*`;
- leave missing optional dependencies as explicit gaps instead of fabricating them;
- avoid private vaults, account data, plugin caches, browser profiles, tokens, and personal workflow history.

## Runtime Expectations

- Python 3.11+ recommended.
- No background daemon is required.
- Scripts are invoked at governed boundaries; they do not replace the text-first legal chain.
- Public workflow storage is created by the user, not bundled from the maintainer's machine.

## Portable Workspace Setup

Suggested baseline:

```bash
export SXLB_HOME="$CODEX_SKILLS_HOME/sxlb"
export SXLB_CASE_ROOT="$HOME/sxlb-cases"
export SXLB_GUOSHIGUAN_INDEX="$SXLB_CASE_ROOT/guoshiguan/index.md"
export SXLB_REFERENCE_POOL="$HOME/sxlb-reference-pool"

mkdir -p "$SXLB_CASE_ROOT/guoshiguan"
mkdir -p "$SXLB_REFERENCE_POOL/omx/upstream" "$SXLB_REFERENCE_POOL/omx/extracted" "$SXLB_REFERENCE_POOL/omx/evaluations"
cp "$SXLB_HOME/templates/guoshiguan-index.md" "$SXLB_GUOSHIGUAN_INDEX"
cp "$SXLB_HOME/templates/hanlinyuan-manifest.md" "$SXLB_REFERENCE_POOL/README.md"
```

These folders are empty operating surfaces. They are not a copy of the maintainer's private history.

## Optional Integrations

Optional integrations should be installed separately by the user:

- GitHub CLI for release workflows
- Browser/Chrome tools for UI verification
- document/spreadsheet/design plugins for artifact workflows

Private memory systems are not required for the public edition. The public package includes the workflow protocols and templates; users may connect their own memory, note, or worklog stores later.

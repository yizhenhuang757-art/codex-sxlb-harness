# Privacy And Publication Boundary

This workspace exists to prevent accidental publication of the private operating environment.

## Never Publish

- absolute personal paths
- private vault paths
- private case/worklog history
- internal wiki or 国史馆 source material
- email, TickTick, Zotero, browser, or plugin cache data
- credentials, browser profiles, or MCP config
- generated `__pycache__` and `*.pyc`
- full local `skill-inventory.generated.md`

## Public Placeholders

Use these placeholders in docs and source:

```text
$SXLB_HOME
$SXLB_CASE_ROOT
$SXLB_GUOSHIGUAN_INDEX
$SXLB_REFERENCE_POOL
$CODEX_HOME
$CODEX_SKILLS_HOME
```

`HYZ` is the intended public project namespace and is not treated as private data by itself.

## Publishable Without Private Data

The following are public-safe when shipped as protocols, templates, empty indexes, or adapter boundaries:

- 案卷 templates and closure gates
- 国史馆 catalog pattern and blank index
- 起居郎 writeback protocol and candidate format
- 翰林院 reference-pool manifest and admission workflow
- status-board scripts and response-board checks
- scanners and review protocols for external project absorption

## Publication Gate

Before any GitHub public switch:

```bash
rg -n "personal-path|private-vault|private-case-root|private-chat-record|credential|secret" .
```

Matches are allowed only in privacy docs or test fixtures that explicitly assert forbidden examples.

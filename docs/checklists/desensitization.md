# Desensitization Checklist

## Source Files

- [x] Remove `__pycache__` and `*.pyc`.
- [x] Replace local absolute paths with environment variables.
- [x] Remove private worklog examples or turn them into synthetic examples.
- [x] Replace full local skill inventory with a curated sample inventory.
- [x] Confirm scripts do not read private config by default.
- [x] Move duplicate staging directory out of the public workspace.

## Documentation

- [x] Use `inspired by` for Edict/OpenClaw attribution.
- [x] Avoid copying external README prose beyond short attributed references.
- [x] Explain that public edition is independent and does not vendor Edict/OpenClaw source.
- [x] Document optional plugins without copying plugin cache content.
- [x] Document portable workflow scope separately from private data.

## Verification

- [x] Run unit tests.
- [x] Run absolute path scan.
- [x] Run credential keyword scan.
- [x] Add draft license.
- [x] Draft CI workflow under `docs/ci/test-workflow.yml`.
- [ ] Activate CI under `.github/workflows/` after GitHub token has `workflow` scope.
- [x] Confirm final license/owner before public release.
- [x] Keep repository private until verification checks pass.

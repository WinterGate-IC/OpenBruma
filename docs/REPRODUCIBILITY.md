# Reproducibility

- Build uses `mkarchiso` with pinned package versions from Arch repos.
- Arch is a rolling release; exact reproducibility requires a snapshot mirror
  (e.g. https://archive.archlinux.org) and a fixed date.
- Set `SOURCE_DATE_EPOCH` for deterministic timestamps in profiledef.sh.
- Record the Arch mirror snapshot date used in release notes.

## CI
See .github/workflows/build.yml for automated build notes (manual trigger).
Building Arch ISOs in CI requires an Arch environment; the workflow documents
the steps rather than running fully in GitHub-hosted runners.

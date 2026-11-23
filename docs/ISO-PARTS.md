# Downloading the split ISO

The v0.2.0 GitHub Release publishes the ISO in 250 MB parts because the
upload connection to GitHub is limited. Reassemble them before use.

## Files

- `openbruma-amd64.hybrid.iso.part-aa` … `part-ai`
- `SHA256SUMS.parts` — per-part checksums
- Final ISO SHA-256:
  `a9c8bf0329e40a88a0777f4fac0b4f92b2169fdc82cd7ed82d9228d206b7503d`

## Reassemble (Linux/macOS)

```sh
cat openbruma-amd64.hybrid.iso.part-* > openbruma-amd64.hybrid.iso
sha256sum -c SHA256SUMS.parts
sha256sum openbruma-amd64.hybrid.iso
```

## Reassemble (Windows PowerShell)

```powershell
Get-ChildItem openbruma-amd64.hybrid.iso.part-* |
  Sort-Object Name |
  ForEach-Object { Get-Content $_.FullName -AsByteStream -Raw } |
  Set-Content openbruma-amd64.hybrid.iso -AsByteStream
Get-FileHash openbruma-amd64.hybrid.iso -Algorithm SHA256
```

The final hash must match
`a9c8bf0329e40a88a0777f4fac0b4f92b2169fdc82cd7ed82d9228d206b7503d`.

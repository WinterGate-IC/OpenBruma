# Downloading the ISO

Releases publish the full ISO when the upload succeeds, and always provide a
250 MB split copy as a fallback. Reassemble the parts before use.

## Files

- `openbruma-amd64.hybrid.iso.part-*` (250 MB parts)
- `SHA256SUMS.debian` — checksum of the full ISO
- `SHA256SUMS.parts` — per-part checksums
- `REASSEMBLE.txt` — short instructions

Final ISO SHA-256:
`c5f084837fce82b40a6a8ce2e294c85c53c3d51154a08fe76ff63947c04abd6c`

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
`c5f084837fce82b40a6a8ce2e294c85c53c3d51154a08fe76ff63947c04abd6c`.

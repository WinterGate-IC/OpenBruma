# OpenBruma Case Capsule

Case Capsule is OpenBruma 0.4.0's headline feature: every investigation gets its
own **encrypted case workspace** with an automatic, **tamper-evident chain of
custody**. It is part of the desktop, not a separate web service.

> Use it for lawful, documented and proportional work only. Case Capsule creates
> tamper-evident documentation. It is **not** a certified forensic product and
> does not by itself establish court admissibility.

## What it does

- **Encrypted at rest** — each case is a `gocryptfs` vault under your home
  directory. If `gocryptfs` is unavailable, Case Capsule falls back to an
  encrypted archive (`gpg` AES-256, `age` when GPG is missing) plus a temporary
  working directory that is wiped when the case is closed or sealed.
- **Logged case terminal** — `bruma shell` opens an opt-in shell whose commands,
  working directory, duration and exit code are recorded. Only that shell (and
  `bruma run`) is instrumented; normal terminals are untouched.
- **Automatic artifact hashing** — files and URLs registered as evidence are
  copied into the vault and SHA-256 hashed.
- **Hash-chained timeline** — every event is linked:
  `event_hash = SHA-256(canonical_json(event_without_hash) + previous_hash)`.
  Deleting, reordering or editing an event breaks the chain and is reported.
- **Seal and export** — produces `case.json`, `timeline.json`,
  `artifacts.json`, `tool_runs.json`, `notes.json`, a self-contained
  `report.html`, `SHA256SUMS`, an optional GPG signature, then encrypts the
  bundle and unmounts the vault.
- **Verify** — `bruma case verify bundle` decrypts to a temporary directory,
  recomputes every hash and checks the artifacts and checksums.

No cloud. No telemetry. No external API calls (a URL is fetched only when the
operator explicitly registers it as evidence).

## Install (inside OpenBruma)

Case Capsule ships in the ISO. Packages used: `gocryptfs`, `age`, `sqlite3`,
`python3-gi`, `gir1.2-gtk-3.0`, `gnupg`, `zstd`, `fuse3`.

Launch it from **Applications → System → Case Capsule**, from the panel button,
or use the CLI.

## CLI

```text
bruma case new <title> [--operator NAME] [--scope TEXT] [--id ID]
bruma case open <case-id>
bruma case close
bruma case status
bruma case list
bruma shell
bruma run -- <command>
bruma run --tool <tool> -- <args...>
bruma note <text>
bruma evidence add <path-or-url> [--notes TEXT]
bruma case seal [--notes TEXT]
bruma case verify <bundle>
bruma case export <case-id> --html --json
```

The passphrase is asked on the terminal, or read from stdin when no terminal is
available (automation/tests). It is never written to disk, shell history,
process arguments or the environment.

## Example session

```console
$ bruma case new "Demo - example.com reconnaissance" --operator "demo operator"
Case passphrase: ********
Confirm passphrase: ********
Created case case-20261126-143426-c08ee9
Backend: gocryptfs

$ bruma case open case-20261126-143426-c08ee9
Case passphrase: ********
Opened case-20261126-143426-c08ee9 (gocryptfs)

$ bruma shell
OpenBruma case case-20261126-143426-c08ee9 - commands are recorded.
(case case-20261126-143426-c08ee9) analyst@openbruma:~$ whois example.com
...
(case case-20261126-143426-c08ee9) analyst@openbruma:~$ exit

$ bruma evidence add ./screenshot.png --notes "landing page"
Registered evidence /home/analyst/screenshot.png
SHA-256: 786bda1ee041f80ee63fff5ab74cf562e43d3d76ee00f18550302c94c5e00bfc

$ bruma note "DNS confirmed; no further action"

$ bruma case seal
Case passphrase: ********
Confirm passphrase: ********
Sealed case case-20261126-143426-c08ee9
Events:   5
Artifacts:3
Root:     16a6227b9796cb12cb407d2daff49d9cdf0f107f7d4da60ad74eeba278f6f39d
Bundle:   /home/analyst/OpenBruma-Cases/case-...-sealed-....tar.xz.gpg
```

Verification (from the demo run used for this document):

```console
$ bruma case verify case-...-sealed-....tar.xz.gpg
Case passphrase: ********
Verify: PASS
Case:   case-20261126-143426-c08ee9
Events: 5
Root:   16a6227b9796cb12cb407d2daff49d9cdf0f107f7d4da60ad74eeba278f6f39d
```

## Data model (SQLite inside the vault)

| Table | Purpose |
| --- | --- |
| `cases` | case id, title, operator, created, scope, host, version |
| `events` | `seq`, `event_id`, UTC timestamp, type, operator, host, payload JSON, `previous_hash`, `event_hash` |
| `artifacts` | path/URL, size, MIME, SHA-256, first seen, source, notes, event id |
| `notes` | free-text notes linked to events |
| `tool_runs` | argv, exit code, duration, cwd, stdout/stderr paths and hashes |
| `seals` | sealed time, root hash, event/artifact counts, bundle path, signature |

Chain rule:

```
previous_hash(0) = "GENESIS"
event_hash(n)    = SHA-256(canonical_json(event_n) + event_hash(n-1))
root_hash        = event_hash(last event)
```

`canonical_json` is sorted-key, compact JSON. Verification also checks that
`seq` is contiguous, so deleted events are detected even if hashes were somehow
recomputed.

## Sealed bundle

`~/OpenBruma-Cases/<case-id>-sealed-<timestamp>.tar.xz.gpg` (or `.age`):

```text
case.json          metadata, root hash, counts, legal notice
timeline.json      full event chain
artifacts.json     registered artifacts and hashes
tool_runs.json     captured command runs
notes.json         notes
report.html        offline, self-contained report
SHA256SUMS         checksums of the files above
SHA256SUMS.asc     detached GPG signature (when a secret key exists)
artifacts/         the evidence files themselves
```

By default the plaintext export directory is deleted after encryption. Use
`--keep-plaintext` only when you deliberately want the unencrypted copy.

## Case terminal details

- Enabled only through `bruma shell` (an opt-in shell with a generated rcfile)
  or `bruma run`.
- Captures command line, cwd, exit code and duration via bash `DEBUG`/`PROMPT_COMMAND`
  hooks and stores a `script(1)` transcript in the vault.
- Adds case-aware wrappers to `PATH` **inside that shell only** for:
  `maigret`, `sherlock`, `holehe`, `blackbird`, `h8mail`, `nmap`, `whois`,
  `dig`, `exiftool`, `tshark`, `wireshark-cli`, `binwalk`, `mat2`.
- `bruma run -- <cmd>` captures stdout/stderr verbatim (stored and hashed),
  which is the precise way to record a single tool invocation.

## Security notes and limitations

- Rootless: no `sudo` required; vaults live under `~/.local/share/bruma`.
- Encrypted at rest; the passphrase is never persisted. Forgetting it means the
  case cannot be recovered.
- `gocryptfs` protects data at rest. While a case is open it is readable by your
  user account and by anything running as you; close or seal cases when idle.
- The logged shell records commands and transcripts, not kernel-level activity.
  It is documentation, not full endpoint monitoring.
- The chain detects modification of the case database/events. It does not defend
  against an attacker who has your passphrase and rewrites the entire chain
  before sealing; seal promptly and keep the sealed bundle elsewhere.
- GPG signing uses the first available secret key (`gpg --detach-sign`).
- Report generation is offline and self-contained; no assets are fetched.
- Case Capsule is not certified forensic software and makes no admissibility
  claim.

## Tests

`case-capsule/tests/run_tests.sh` covers: create/open, evidence, notes,
`bruma run whois example.com`, chain verification, seal, verify, wrong
passphrase refusal, event tampering detection, seal refusal on a broken chain,
plaintext cleanup, and that normal terminals are not instrumented.

Latest run: **ALL TESTS PASSED** (gocryptfs backend, Debian 13).

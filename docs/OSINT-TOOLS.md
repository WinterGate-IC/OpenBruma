# OpenBruma OSINT toolchain

OpenBruma ships a curated set of lawful, publicly available investigative
tools. These are standard Debian packages; OpenBruma does not modify their
behaviour.

## Network and DNS reconnaissance
- `nmap` — port/service discovery
- `masscan` — high-speed port scanning
- `dnsutils` (`dig`, `nslookup`) — DNS queries
- `dnsrecon` — DNS enumeration
- `whois` — registration data
- `traceroute`, `mtr-tiny` — path analysis
- `gobuster`, `dirb` — content/directory discovery
- `httrack` — website mirroring
- `w3m`, `lynx` — text browsers

## Traffic analysis
- `tcpdump` — packet capture
- `wireshark`, `tshark` — protocol analysis

## Media and metadata
- `exiftool` — metadata inspection
- `mat2` — metadata removal
- `binwalk` — firmware/embedded file analysis
- `foremost`, `scalpel` — file carving
- `sleuthkit` (`fls`, `icat`, `tsk_recover`) — filesystem forensics
- `forensics-all`, `forensics-extra` — Debian forensic metapackages

## Credential and hash work (authorised testing only)
- `john` — password auditing
- `hashcat` — hash recovery
- `hydra` — authentication testing

These tools must only be used against systems you own or are explicitly
authorised to test.

## Productivity
- Firefox ESR, Thunderbird, LibreOffice, Evince, file-roller

## Boundaries

OpenBruma is built for lawful, documented, proportional investigative work.
It is not a hacking, harassment, doxing, or vigilante toolkit. See
`SECURITY.md` and the WinterGateIC operating notice. Users are responsible
for complying with applicable law and the collective's code of conduct.

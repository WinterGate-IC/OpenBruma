# OpenBruma

**OpenBruma is the official Linux distribution of the WinterGate Intelligence
Collective (WinterGateIC).** It is a ready-to-run, Debian-based desktop OS for
lawful open-source intelligence (OSINT), investigative research, digital
forensics and defensive security work — with the everyday apps and hardware
support you expect from a normal Linux desktop.

It boots live from a USB stick, installs to a disk, USB drive or virtual
machine with a **branded graphical installer**, and starts you on a complete
XFCE desktop with a neon identity, a live wallpaper and the tools already
installed and organised. Nothing has to be set up by hand: Wi-Fi, Bluetooth,
audio, browsers, office apps and the OSINT/OPSEC suites are there on first boot.

> OpenBruma is a **distribution**, not a from-scratch operating system. It is
> built on Debian 13 ("trixie") and uses Debian's kernel, drivers and packages.

---

## What is in the box

| Area | What you get |
| --- | --- |
| **Desktop** | XFCE 4.20, single neon top bar, Arc-Dark + Papirus-Dark, dark by default (light theme available in *Settings → Appearance*) |
| **Live wallpapers** | Three dimmed animated backgrounds (Aurora Drift, Data Rain, Ember Pulse) with the official OpenBruma logo; Aurora Drift is the default |
| **Theme presets** | Neo-Noir, Synthwave Violet, Crimson Circuit, Cyber-Lime and Ghost Protocol via *OpenBruma Themes* |
| **Installer** | Calamares: Guided (erase disk), Custom (manual partitioning) and USB / Virtual Machine |
| **Network** | NetworkManager + Wi-Fi applet, Blueman, firmware for Intel / Realtek / Atheros / Broadcom, radios unblocked at login |
| **Everyday apps** | Firefox ESR (pinned), Thunderbird, LibreOffice, Parole media player, Ristretto, GParted, archive tools |
| **OSINT & Investigation** | Maigret, Holehe, Blackbird, Sherlock, h8mail, Social Analyzer, Toutatis, Instaloader, waymore, SploitScan, plus nmap, masscan, whois, dnsrecon, gobuster, Wireshark/tshark, exiftool, mat2, binwalk, SleuthKit and forensics-all |
| **OPSEC** | AnonSurf (CLI and graphical), bundled Tor Browser, Tor + torsocks, Nyx, OnionShare, Proxychains, KeePassXC, BleachBit, MAT2, MAC Changer, secure-delete |
| **Dev / scripting** | Python 3 with pip, venv and pipx; an isolated `/opt/osint` environment with normal command wrappers |
| **Hardware** | UEFI (Secure Boot shim) and legacy BIOS, VirtualBox/VMware/QEMU guest tools, x86_64 only |
| **Performance** | zram swap, earlyoom, preload, irqbalance and a tuned desktop profile |

The **WIC Apps** menu (UmbraForge, VoiceForge, Ominis OSINT, Coeus OSINT
ToolBox and the WIC portal) is separate from the general OSINT suite; it is the
collective's own tooling.

---

## Download

Releases are published on the
[Releases page](https://github.com/WinterGate-IC/OpenBruma/releases).

Each release provides:

- `openbruma-amd64.hybrid.iso` — the full ISO (when the upload allows it), and
- `openbruma-amd64.hybrid.iso.part-*` + `SHA256SUMS.parts` + `REASSEMBLE.txt`
  as a fallback split into 250 MB pieces.

Verify before booting:

```sh
sha256sum -c SHA256SUMS.debian     # full ISO
# or, for split downloads:
cat openbruma-amd64.hybrid.iso.part-* > openbruma-amd64.hybrid.iso
sha256sum -c SHA256SUMS.parts
```

Write the image with `dd`, balenaEtcher, Rufus (DD mode) or Ventoy. The ISO is
hybrid: it boots from USB and from a DVD, on UEFI and BIOS.

---

## Install

The installer is on the desktop and in **Applications → System**:

1. **Install OpenBruma (Guided)** — pick a disk, everything else is automatic.
2. **Install OpenBruma (Custom)** — manual partitioning for dual-boot, LUKS or
   a specific layout.
3. **Install OpenBruma (USB / Virtual Machine)** — guided install where the
   target device is always chosen explicitly, so you can install onto a USB
   stick or a VirtualBox/VMware virtual disk without touching your main drive.

Installed systems boot to the LightDM greeter. The live account is removed
during installation; the **root** account remains and your chosen user is
created with sudo access. Add more accounts later with **Users and Groups**.

### Live credentials

| Account | Username | Password |
| --- | --- | --- |
| Live session | `openbruma` | `openbruma` |
| Root | `root` | `openbruma` |

The live user has passwordless `sudo`; `sudo` works normally after install for
the user you create.

---

## Security and legal boundaries

OpenBruma exists for **lawful, documented, proportional** investigative work:
journalism, due diligence, fraud and threat research, incident response,
digital forensics and privacy protection. It is **not** a hacking, harassment
or vigilante toolkit. See [`SECURITY.md`](SECURITY.md) and the WinterGateIC
public notice for the collective's operating rules.

OPSEC tooling (Tor, AnonSurf, Proxychains) is included for privacy and
research; you are responsible for complying with the law where you live and
with the terms of the services you use.

---

## Base and compatibility

- **Base:** Debian 13 "trixie", x86_64, built reproducibly with `live-build`.
- **Kernel:** Debian `linux-image-amd64` (6.12 series).
- **Boot:** UEFI with the Debian shim (Secure Boot) and legacy BIOS.
- **Architecture:** 64-bit only. A future *OpenBruma Legacy* edition for 32-bit
  machines is planned; the old Arch-based prototype is kept under `archiso/`
  for reference only.

---

## Build from source

Full instructions: [`docs/DEBIAN.md`](docs/DEBIAN.md). Summary:

```sh
apt-get install live-build debootstrap squashfs-tools xorriso \
  isolinux syslinux-common grub-efi-amd64-bin grub-pc-bin mtools dosfstools

cp -a OpenBruma /root/OpenBruma
REPO_DIR=/root/OpenBruma \
BUILD_DIR=/root/openbruma-debian-build \
OUT_DIR=/root/openbruma-debian-out \
bash /root/OpenBruma/debian/build.sh
```

The ISO and its SHA-256 are printed at the end of the build.

---

## Repository layout

```
OpenBruma/
  README.md
  CHANGELOG.md
  SECURITY.md
  debian/            # live-build profile (current release)
    auto/config
    config/          # package lists, includes, hooks, Calamares config
    build.sh
  branding/          # logos, wallpapers, fonts, live wallpaper generator
  docs/              # build, testing, checksums, licensing, ISO parts
  build/             # host helpers (VM creation, ISO download)
  archiso/           # legacy Arch prototype (reference only)
  installer/         # legacy installer reference configs
  packages/          # package notes
  scripts/           # release/ISO helpers
```

---

## Credits and license

Project scripts, configuration and branding: MIT (see [`LICENSE`](LICENSE)).
Bundled Debian packages keep their own licenses — see
[`docs/LICENSES.md`](docs/LICENSES.md). The OpenBruma and WinterGateIC logos
are marks of WinterGate IC, used for official OpenBruma builds only.

Built with Debian, XFCE, Calamares, Tor, Parrot's AnonSurf, and the great
open-source OSINT community (Maigret, Holehe, Blackbird, Sherlock and friends).

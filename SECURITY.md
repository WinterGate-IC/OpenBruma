# Security Policy

## Reporting

Report security issues privately to the maintainers. Do not open public
issues for undisclosed vulnerabilities.

## Secrets

- No secrets, private keys, or credentials are committed to this repository.
- Build VMs are disposable; credentials used inside them are throwaway.
- The GitHub token used for publishing is stored in the host credential
  store only and is never committed.

## Firmware / drivers

- Only firmware/drivers whose redistribution terms are clearly permitted are
  included. See docs/LICENSES.md.
- `linux-firmware` is included for broad hardware support; review its
  license terms before redistributing modified images.

## Host safety

- Building and testing happen only inside disposable VirtualBox VMs.
- No writes to host physical disks, no host bootloader changes, no host
  partitioning.

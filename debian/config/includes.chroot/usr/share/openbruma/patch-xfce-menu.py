#!/usr/bin/env python3
"""Add OpenBruma categories to the XFCE application menu used by Whisker."""
import sys

PATH = "/etc/xdg/menus/xfce-applications.menu"

BLOCK = """
    <!-- OpenBruma custom categories -->
    <Menu>
        <Name>OSINT</Name>
        <Directory>openbruma-osint.directory</Directory>
        <Include>
            <Category>X-OSINT</Category>
        </Include>
    </Menu>

    <Menu>
        <Name>OPSEC</Name>
        <Directory>openbruma-opsec.directory</Directory>
        <Include>
            <Category>X-OPSEC</Category>
        </Include>
    </Menu>

    <Menu>
        <Name>WIC</Name>
        <Directory>wic-apps.directory</Directory>
        <Include>
            <Category>WIC</Category>
        </Include>
    </Menu>

"""

try:
    with open(PATH, encoding="utf-8") as fh:
        data = fh.read()
except OSError:
    sys.exit(0)

if "X-OSINT" in data:
    print("already patched")
    sys.exit(0)

idx = data.rfind("</Menu>")
if idx == -1:
    sys.exit(0)

data = data[:idx] + BLOCK + data[idx:]
with open(PATH, "w", encoding="utf-8") as fh:
    fh.write(data)
print("menu patched")

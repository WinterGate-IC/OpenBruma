#!/usr/bin/env python3
"""OpenBruma Case Capsule - GTK front-end for the bruma CLI."""
import os
import subprocess
import sys

try:
    import gi
    gi.require_version("Gtk", "3.0")
    from gi.repository import Gtk
except Exception:
    sys.stderr.write("Case Capsule GUI requires python3-gi and GTK3\n")
    sys.exit(1)

BRUMA = "/usr/local/bin/bruma"
if not os.path.exists(BRUMA):
    BRUMA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "bruma")


def run_bruma(args, stdin_text=None):
    cmd = [sys.executable, BRUMA] + args if BRUMA.endswith(".py") else [BRUMA] + args
    try:
        res = subprocess.run(cmd, input=stdin_text, capture_output=True, text=True, timeout=1800)
        return res.returncode, (res.stdout or "") + (res.stderr or "")
    except Exception as exc:
        return 1, str(exc)


def info(parent, title, text):
    dlg = Gtk.MessageDialog(parent=parent, modal=True, message_type=Gtk.MessageType.INFO,
                            buttons=Gtk.ButtonsType.OK, text=title)
    dlg.format_secondary_text(text[:4000])
    dlg.run()
    dlg.destroy()


def ask_pass(parent, title, confirm=False):
    dlg = Gtk.Dialog(title=title, parent=parent, modal=True,
                     buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                              Gtk.STOCK_OK, Gtk.ResponseType.OK))
    box = dlg.get_content_area()
    box.set_spacing(6)
    box.set_border_width(12)
    p1 = Gtk.Entry(visibility=False, placeholder_text="Case passphrase")
    box.add(p1)
    p2 = None
    if confirm:
        p2 = Gtk.Entry(visibility=False, placeholder_text="Confirm passphrase")
        box.add(p2)
    dlg.show_all()
    resp = dlg.run()
    a = p1.get_text()
    b = p2.get_text() if p2 else a
    dlg.destroy()
    if resp != Gtk.ResponseType.OK:
        return None
    if not a or a != b:
        info(parent, "Passphrase", "Passphrases are empty or do not match.")
        return None
    return a


class Capsule(Gtk.Window):
    def __init__(self):
        super().__init__(title="OpenBruma Case Capsule")
        self.set_default_size(560, 380)
        self.set_border_width(12)
        outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.add(outer)

        title = Gtk.Label()
        title.set_markup("<span size='x-large' weight='bold' color='#00ff9d'>Case Capsule</span>")
        outer.pack_start(title, False, False, 0)
        sub = Gtk.Label(label="Encrypted case workspace with a tamper-evident chain of custody")
        sub.set_line_wrap(True)
        outer.pack_start(sub, False, False, 0)

        self.status = Gtk.Label(label="Checking...")
        self.status.set_line_wrap(True)
        self.status.set_xalign(0)
        frame = Gtk.Frame(label="Status")
        frame.add(self.status)
        outer.pack_start(frame, False, False, 0)

        grid = Gtk.Grid(column_spacing=8, row_spacing=8)
        outer.pack_start(grid, False, False, 0)
        buttons = [
            ("New Case", self.on_new),
            ("Open Case", self.on_open),
            ("Case Terminal", self.on_shell),
            ("Add Evidence", self.on_evidence),
            ("Add Note", self.on_note),
            ("Seal Case", self.on_seal),
            ("Verify Bundle", self.on_verify),
            ("Export Report", self.on_export),
            ("Close Case", self.on_close),
            ("Refresh", self.refresh),
        ]
        for i, (label, cb) in enumerate(buttons):
            btn = Gtk.Button(label=label)
            btn.connect("clicked", cb)
            btn.set_hexpand(True)
            grid.attach(btn, i % 2, i // 2, 1, 1)

        notice = Gtk.Label()
        notice.set_markup("<span size='small'>Lawful, documented, proportional use only. "
                          "Tamper-evident documentation, not a certified forensic product.</span>")
        notice.set_line_wrap(True)
        outer.pack_end(notice, False, False, 0)

        self.refresh()

    def refresh(self, *_):
        code, out = run_bruma(["case", "status"])
        self.status.set_text(out.strip() or "No case is open.")

    def on_new(self, *_):
        dlg = Gtk.Dialog(title="New case", parent=self, modal=True,
                         buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                  Gtk.STOCK_OK, Gtk.ResponseType.OK))
        box = dlg.get_content_area()
        box.set_spacing(6)
        box.set_border_width(12)
        fields = {}
        for key, label in (("title", "Case title"), ("operator", "Operator"), ("scope", "Scope (optional)")):
            box.add(Gtk.Label(label=label, xalign=0))
            entry = Gtk.Entry()
            fields[key] = entry
            box.add(entry)
        box.add(Gtk.Label(label="Passphrase", xalign=0))
        p1 = Gtk.Entry(visibility=False)
        box.add(p1)
        box.add(Gtk.Label(label="Confirm passphrase", xalign=0))
        p2 = Gtk.Entry(visibility=False)
        box.add(p2)
        dlg.show_all()
        resp = dlg.run()
        title = fields["title"].get_text().strip()
        operator = fields["operator"].get_text().strip()
        scope = fields["scope"].get_text().strip()
        a, b = p1.get_text(), p2.get_text()
        dlg.destroy()
        if resp != Gtk.ResponseType.OK:
            return
        if not title or not a or a != b:
            info(self, "New case", "Title and matching passphrases are required.")
            return
        args = ["case", "new", title, "--scope", scope]
        if operator:
            args += ["--operator", operator]
        code, out = run_bruma(args, stdin_text=a + "\n" + a + "\n")
        info(self, "New case", out)
        self.refresh()

    def on_open(self, *_):
        code, out = run_bruma(["case", "list"])
        ids = [line.split()[1] for line in out.splitlines() if line.strip() and not line.startswith("No cases")]
        if not ids:
            info(self, "Open case", "No cases found. Create one first.")
            return
        dlg = Gtk.Dialog(title="Open case", parent=self, modal=True,
                         buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                  Gtk.STOCK_OK, Gtk.ResponseType.OK))
        box = dlg.get_content_area()
        box.set_spacing(6)
        box.set_border_width(12)
        combo = Gtk.ComboBoxText()
        for cid in ids:
            combo.append_text(cid)
        combo.set_active(0)
        box.add(combo)
        box.add(Gtk.Label(label="Passphrase", xalign=0))
        pw = Gtk.Entry(visibility=False)
        box.add(pw)
        dlg.show_all()
        resp = dlg.run()
        cid = combo.get_active_text()
        passphrase = pw.get_text()
        dlg.destroy()
        if resp != Gtk.ResponseType.OK or not cid:
            return
        code, out = run_bruma(["case", "open", cid], stdin_text=passphrase + "\n")
        info(self, "Open case", out)
        self.refresh()

    def on_shell(self, *_):
        code, out = run_bruma(["case", "status"])
        if "No case is open" in out:
            info(self, "Case terminal", "Open a case first.")
            return
        subprocess.Popen(["xfce4-terminal", "--title", "OpenBruma Case Terminal",
                          "--command", BRUMA + " shell"])

    def on_evidence(self, *_):
        dlg = Gtk.Dialog(title="Add evidence", parent=self, modal=True,
                         buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                  Gtk.STOCK_OK, Gtk.ResponseType.OK))
        box = dlg.get_content_area()
        box.set_spacing(6)
        box.set_border_width(12)
        box.add(Gtk.Label(label="File path or URL", xalign=0))
        target = Gtk.Entry()
        box.add(target)
        choose = Gtk.Button(label="Choose file...")

        def pick(*_):
            fc = Gtk.FileChooserDialog(title="Evidence file", parent=dlg,
                                       action=Gtk.FileChooserAction.OPEN,
                                       buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                                Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
            if fc.run() == Gtk.ResponseType.OK:
                target.set_text(fc.get_filename())
            fc.destroy()

        choose.connect("clicked", pick)
        box.add(choose)
        box.add(Gtk.Label(label="Notes (optional)", xalign=0))
        notes = Gtk.Entry()
        box.add(notes)
        dlg.show_all()
        resp = dlg.run()
        value = target.get_text().strip()
        note = notes.get_text().strip()
        dlg.destroy()
        if resp != Gtk.ResponseType.OK or not value:
            return
        code, out = run_bruma(["evidence", "add", value, "--notes", note])
        info(self, "Add evidence", out)

    def on_note(self, *_):
        dlg = Gtk.Dialog(title="Add note", parent=self, modal=True,
                         buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                  Gtk.STOCK_OK, Gtk.ResponseType.OK))
        box = dlg.get_content_area()
        box.set_border_width(12)
        entry = Gtk.Entry()
        box.add(entry)
        dlg.show_all()
        resp = dlg.run()
        text = entry.get_text().strip()
        dlg.destroy()
        if resp != Gtk.ResponseType.OK or not text:
            return
        code, out = run_bruma(["note", text])
        info(self, "Note", out)

    def on_seal(self, *_):
        passphrase = ask_pass(self, "Seal case", confirm=True)
        if not passphrase:
            return
        code, out = run_bruma(["case", "seal"], stdin_text=passphrase + "\n" + passphrase + "\n")
        info(self, "Seal case", out)
        self.refresh()

    def on_verify(self, *_):
        fc = Gtk.FileChooserDialog(title="Sealed case bundle", parent=self,
                                   action=Gtk.FileChooserAction.OPEN,
                                   buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                            Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
        if fc.run() != Gtk.ResponseType.OK:
            fc.destroy()
            return
        bundle = fc.get_filename()
        fc.destroy()
        passphrase = ask_pass(self, "Verify bundle")
        if not passphrase:
            return
        code, out = run_bruma(["case", "verify", bundle], stdin_text=passphrase + "\n")
        info(self, "Verify bundle", out)

    def on_export(self, *_):
        code, out = run_bruma(["case", "export", "current", "--html", "--json"])
        info(self, "Export report", out)

    def on_close(self, *_):
        if info_confirm(self, "Close case", "Close the active case and unmount the vault?"):
            code, out = run_bruma(["case", "close"])
            info(self, "Close case", out)
            self.refresh()


def info_confirm(parent, title, text):
    dlg = Gtk.MessageDialog(parent=parent, modal=True, message_type=Gtk.MessageType.QUESTION,
                            buttons=Gtk.ButtonsType.YES_NO, text=title)
    dlg.format_secondary_text(text)
    resp = dlg.run()
    dlg.destroy()
    return resp == Gtk.ResponseType.YES


def main():
    win = Capsule()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()


if __name__ == "__main__":
    main()

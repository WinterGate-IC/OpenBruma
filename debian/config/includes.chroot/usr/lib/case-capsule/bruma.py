#!/usr/bin/env python3
"""OpenBruma Case Capsule - encrypted, tamper-evident case workspace.

Rootless CLI. No network calls except when the operator explicitly registers a
URL as evidence. Nothing is sent anywhere else. No telemetry.

Data model: SQLite inside the encrypted case directory. Every event is linked
in a SHA-256 hash chain (event_hash = SHA256(canonical_json(event) + prev)).
"""
import argparse
import getpass
import hashlib
import json
import mimetypes
import os
import pty
import re
import select
import shutil
import signal
import sqlite3
import subprocess
import sys
import tarfile
import tempfile
import time
import urllib.request
import uuid
from datetime import datetime, timezone

VERSION = "0.4.0"
APP = "OpenBruma Case Capsule"
BRUMA_HOME = os.path.join(os.path.expanduser("~"), ".local", "share", "bruma")
CASES_DIR = os.path.join(BRUMA_HOME, "cases")
STATE_DIR = os.path.join(os.path.expanduser("~"), ".local", "state", "bruma")
ACTIVE = os.path.join(STATE_DIR, "active.json")
EXPORT_HOME = os.path.join(os.path.expanduser("~"), "OpenBruma-Cases")
CHAIN_START = "GENESIS"
LEGAL = ("For lawful, documented and proportional use only. Case Capsule is "
         "tamper-evident documentation, not a certified forensic product and "
         "not a claim of court admissibility.")


# --------------------------------------------------------------------------
# small helpers
# --------------------------------------------------------------------------
def now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def fail(msg, code=1):
    print("bruma: " + msg, file=sys.stderr)
    sys.exit(code)


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def ensure_dirs():
    for d in (BRUMA_HOME, CASES_DIR, STATE_DIR, EXPORT_HOME):
        os.makedirs(d, mode=0o700, exist_ok=True)
        try:
            os.chmod(d, 0o700)
        except OSError:
            pass


def case_dir(case_id):
    return os.path.join(CASES_DIR, case_id)


def valid_case_id(case_id):
    return bool(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{2,80}", case_id or ""))


def read_active():
    try:
        with open(ACTIVE, encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return None


def write_active(data):
    os.makedirs(STATE_DIR, mode=0o700, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=STATE_DIR)
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        json.dump(data, fh)
    os.chmod(tmp, 0o600)
    os.replace(tmp, ACTIVE)


def clear_active():
    try:
        os.unlink(ACTIVE)
    except OSError:
        pass


def prompt_passphrase(confirm=False, allow_stdin=True):
    if sys.stdin.isatty():
        p1 = getpass.getpass("Case passphrase: ")
        if confirm:
            p2 = getpass.getpass("Confirm passphrase: ")
            if p1 != p2:
                fail("passphrases do not match")
    else:
        if not allow_stdin:
            fail("no terminal for passphrase")
        p1 = sys.stdin.readline().rstrip("\n")
        if confirm:
            p2 = sys.stdin.readline().rstrip("\n")
            if p1 != p2:
                fail("passphrases do not match")
    if len(p1) < 8:
        fail("passphrase must be at least 8 characters")
    if "\n" in p1 or "\r" in p1:
        fail("passphrase must not contain newlines")
    return p1


# --------------------------------------------------------------------------
# encryption backends
# --------------------------------------------------------------------------
def have(binary):
    return shutil.which(binary) is not None


def gocryptfs_available():
    return have("gocryptfs") and (have("fusermount3") or have("fusermount"))


def fd_passfile(passphrase):
    r, w = os.pipe()
    os.write(w, (passphrase + "\n").encode())
    os.close(w)
    return r


def gocryptfs_init(vault, passphrase):
    r = fd_passfile(passphrase)
    try:
        res = subprocess.run(
            ["gocryptfs", "-init", "-q", "-passfile", "/dev/fd/%d" % r, vault],
            pass_fds=(r,), capture_output=True, text=True)
    finally:
        os.close(r)
    if res.returncode != 0:
        fail("gocryptfs init failed: " + (res.stderr.strip() or res.stdout.strip()))


def gocryptfs_mount(vault, mnt, passphrase):
    os.makedirs(mnt, mode=0o700, exist_ok=True)
    r = fd_passfile(passphrase)
    try:
        res = subprocess.run(
            ["gocryptfs", "-q", "-passfile", "/dev/fd/%d" % r, vault, mnt],
            pass_fds=(r,), capture_output=True, text=True)
    finally:
        os.close(r)
    if res.returncode != 0:
        fail("cannot open case (wrong passphrase or mount problem): "
             + (res.stderr.strip() or res.stdout.strip()))


def gocryptfs_unmount(mnt):
    for cmd in (["fusermount3", "-u", mnt], ["fusermount", "-u", mnt], ["umount", mnt]):
        if have(cmd[0]):
            res = subprocess.run(cmd, capture_output=True, text=True)
            if res.returncode == 0:
                return True
    return False


def age_available():
    return have("age")


def age_crypt(passphrase, src, dst, decrypt=False):
    """Run age with a passphrase through a pty (age insists on a terminal)."""
    cmd = ["age", "-d", "-o", dst, src] if decrypt else ["age", "-p", "-o", dst, src]
    master, slave = pty.openpty()
    proc = subprocess.Popen(cmd, stdin=slave, stdout=slave, stderr=slave)
    os.close(slave)
    buf = b""
    prompts = 0
    deadline = time.time() + 60
    try:
        while proc.poll() is None and time.time() < deadline:
            r, _, _ = select.select([master], [], [], 0.3)
            if not r:
                continue
            try:
                chunk = os.read(master, 4096)
            except OSError:
                break
            if not chunk:
                break
            buf += chunk
            low = buf.lower()
            if b"passphrase" in low and prompts < (1 if decrypt else 2):
                os.write(master, (passphrase + "\n").encode())
                prompts += 1
                buf = b""
        rc = proc.wait(timeout=20)
    except Exception:
        proc.kill()
        rc = 1
    finally:
        os.close(master)
    if rc != 0 or not os.path.exists(dst):
        fail("age encryption/decryption failed")


def gpg_crypt(passphrase, src, dst, decrypt=False):
    r = fd_passfile(passphrase)
    try:
        if decrypt:
            cmd = ["gpg", "--batch", "--yes", "--passphrase-fd", str(r),
                   "--output", dst, "--decrypt", src]
        else:
            cmd = ["gpg", "--batch", "--yes", "--symmetric", "--cipher-algo", "AES256",
                   "--passphrase-fd", str(r), "--output", dst, src]
        res = subprocess.run(cmd, pass_fds=(r,), capture_output=True, text=True)
    finally:
        os.close(r)
    if res.returncode != 0 or not os.path.exists(dst):
        fail("gpg encryption/decryption failed: " + res.stderr.strip())


def preferred_backend():
    """gpg symmetric is the most reliable non-interactive backend; age is a
    fallback when gpg is unavailable."""
    if have("gpg"):
        return "gpg"
    if age_available():
        return "age"
    return ""


def encrypt_file(passphrase, src, dst, decrypt=False):
    backend = preferred_backend()
    if backend == "gpg":
        gpg_crypt(passphrase, src, dst, decrypt)
    elif backend == "age":
        age_crypt(passphrase, src, dst, decrypt)
    else:
        fail("no encryption backend: install gnupg or age")


# --------------------------------------------------------------------------
# database
# --------------------------------------------------------------------------
SCHEMA = """
PRAGMA journal_mode=DELETE;
CREATE TABLE IF NOT EXISTS cases (
  case_id TEXT PRIMARY KEY, title TEXT NOT NULL, operator TEXT NOT NULL,
  created_utc TEXT NOT NULL, scope TEXT DEFAULT '', notes TEXT DEFAULT '',
  host TEXT NOT NULL, version TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS events (
  seq INTEGER PRIMARY KEY AUTOINCREMENT,
  event_id TEXT UNIQUE NOT NULL, case_id TEXT NOT NULL, ts_utc TEXT NOT NULL,
  type TEXT NOT NULL, operator TEXT NOT NULL, host TEXT NOT NULL,
  payload TEXT NOT NULL, previous_hash TEXT NOT NULL, event_hash TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS artifacts (
  id INTEGER PRIMARY KEY AUTOINCREMENT, case_id TEXT NOT NULL,
  path TEXT NOT NULL, origin TEXT DEFAULT '', size INTEGER DEFAULT 0,
  mime TEXT DEFAULT '', sha256 TEXT NOT NULL, first_seen TEXT NOT NULL,
  source TEXT DEFAULT '', notes TEXT DEFAULT '', event_id TEXT DEFAULT ''
);
CREATE TABLE IF NOT EXISTS notes (
  id INTEGER PRIMARY KEY AUTOINCREMENT, case_id TEXT NOT NULL,
  event_id TEXT NOT NULL, text TEXT NOT NULL, created_utc TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS tool_runs (
  id INTEGER PRIMARY KEY AUTOINCREMENT, case_id TEXT NOT NULL,
  event_id TEXT NOT NULL, argv TEXT NOT NULL, exit_code INTEGER,
  duration_ms INTEGER, cwd TEXT, stdout_path TEXT, stderr_path TEXT,
  stdout_sha256 TEXT, stderr_sha256 TEXT, started_utc TEXT, ended_utc TEXT
);
CREATE TABLE IF NOT EXISTS seals (
  id INTEGER PRIMARY KEY AUTOINCREMENT, case_id TEXT NOT NULL,
  sealed_utc TEXT NOT NULL, root_hash TEXT NOT NULL, event_count INTEGER,
  artifact_count INTEGER, bundle_path TEXT, signature TEXT DEFAULT ''
);
"""


def db_path(case_mount):
    return os.path.join(case_mount, "case.db")


def connect(path):
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    return conn


def create_case_db(path, case_id, title, operator, scope, host):
    conn = connect(path)
    conn.execute(
        "INSERT INTO cases(case_id,title,operator,created_utc,scope,host,version) "
        "VALUES(?,?,?,?,?,?,?)",
        (case_id, title, operator, now(), scope, host, VERSION))
    conn.commit()
    add_event(conn, case_id, "case_created",
              {"title": title, "scope": scope, "version": VERSION}, operator, host)
    conn.commit()
    conn.close()


def add_event(conn, case_id, etype, payload, operator, host):
    row = conn.execute("SELECT event_hash FROM events ORDER BY seq DESC LIMIT 1").fetchone()
    prev = row["event_hash"] if row else CHAIN_START
    ev = {
        "case_id": case_id,
        "event_id": str(uuid.uuid4()),
        "ts_utc": now(),
        "type": etype,
        "operator": operator,
        "host": host,
        "payload": payload,
    }
    digest = sha256_bytes((canonical(ev) + prev).encode("utf-8"))
    conn.execute(
        "INSERT INTO events(event_id,case_id,ts_utc,type,operator,host,payload,"
        "previous_hash,event_hash) VALUES(?,?,?,?,?,?,?,?,?)",
        (ev["event_id"], case_id, ev["ts_utc"], etype, operator, host,
         canonical(payload), prev, digest))
    conn.commit()
    return ev["event_id"], digest


def current_operator(conn=None):
    return os.environ.get("BRUMA_OPERATOR") or os.environ.get("USER") or getpass.getuser()


def require_active():
    act = read_active()
    if not act:
        fail("no open case (use: bruma case open <case-id>)")
    if not os.path.isdir(act.get("root", "")):
        fail("active case directory is missing")
    db = db_path(act["root"])
    if not os.path.exists(db):
        fail("case database is missing")
    return act, db


def chain_state(conn):
    rows = conn.execute("SELECT * FROM events ORDER BY seq").fetchall()
    prev = CHAIN_START
    problems = []
    expected_seq = 1
    for row in rows:
        if row["seq"] != expected_seq:
            problems.append("event sequence gap at seq %s (expected %s)" % (row["seq"], expected_seq))
        expected_seq = row["seq"] + 1
        ev = {
            "case_id": row["case_id"], "event_id": row["event_id"],
            "ts_utc": row["ts_utc"], "type": row["type"],
            "operator": row["operator"], "host": row["host"],
            "payload": json.loads(row["payload"]),
        }
        digest = sha256_bytes((canonical(ev) + prev).encode("utf-8"))
        if digest != row["event_hash"]:
            problems.append("event %s hash mismatch" % row["event_id"])
        if row["previous_hash"] != prev:
            problems.append("event %s previous_hash mismatch" % row["event_id"])
        prev = row["event_hash"]
    return {"ok": not problems, "problems": problems, "root": prev, "count": len(rows)}


# --------------------------------------------------------------------------
# case lifecycle
# --------------------------------------------------------------------------
def cmd_case_new(args):
    ensure_dirs()
    title = args.title.strip()
    if not title:
        fail("title required")
    operator = args.operator or current_operator()
    scope = args.scope or ""
    passphrase = prompt_passphrase(confirm=True)
    case_id = args.id or ("case-" + datetime.now().strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:6])
    if not valid_case_id(case_id):
        fail("invalid case id")
    cdir = case_dir(case_id)
    if os.path.exists(cdir):
        fail("case already exists: " + case_id)
    os.makedirs(cdir, mode=0o700)

    backend = "gocryptfs" if gocryptfs_available() else "bundle"
    meta = {"case_id": case_id, "created_utc": now(), "backend": backend}
    with open(os.path.join(cdir, "case.meta"), "w", encoding="utf-8") as fh:
        json.dump(meta, fh)
    os.chmod(os.path.join(cdir, "case.meta"), 0o600)

    if backend == "gocryptfs":
        vault = os.path.join(cdir, "vault")
        mnt = os.path.join(cdir, "mnt")
        os.makedirs(vault, mode=0o700)
        gocryptfs_init(vault, passphrase)
        gocryptfs_mount(vault, mnt, passphrase)
        try:
            create_case_db(db_path(mnt), case_id, title, operator, scope, os.uname().nodename)
        finally:
            gocryptfs_unmount(mnt)
    else:
        work = tempfile.mkdtemp(prefix="bruma-new-", dir=os.environ.get("XDG_RUNTIME_DIR") or "/tmp")
        os.chmod(work, 0o700)
        try:
            create_case_db(db_path(work), case_id, title, operator, scope, os.uname().nodename)
            pack_workdir(cdir, work, passphrase)
        finally:
            shutil.rmtree(work, ignore_errors=True)

    print("Created case %s" % case_id)
    print("Backend: %s" % backend)
    print("Open it with: bruma case open %s" % case_id)


def pack_workdir(cdir, work, passphrase):
    tmp = tempfile.mkdtemp(prefix="bruma-pack-", dir=os.environ.get("XDG_RUNTIME_DIR") or "/tmp")
    os.chmod(tmp, 0o700)
    try:
        tarpath = os.path.join(tmp, "vault.tar.xz")
        with tarfile.open(tarpath, "w:xz") as tar:
            for name in os.listdir(work):
                tar.add(os.path.join(work, name), arcname=name)
        out = os.path.join(cdir, "vault.tar.xz.gpg" if preferred_backend() == "gpg" else "vault.tar.xz.age")
        encrypt_file(passphrase, tarpath, out, decrypt=False)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def unpack_workdir(cdir, passphrase):
    src = None
    for name in ("vault.tar.xz.age", "vault.tar.xz.gpg"):
        if os.path.exists(os.path.join(cdir, name)):
            src = os.path.join(cdir, name)
            break
    if not src:
        fail("case bundle not found")
    work = tempfile.mkdtemp(prefix="bruma-", dir=os.environ.get("XDG_RUNTIME_DIR") or "/tmp")
    os.chmod(work, 0o700)
    tarpath = os.path.join(work, "vault.tar.xz")
    if src.endswith(".age"):
        age_crypt(passphrase, src, tarpath, decrypt=True)
    else:
        gpg_crypt(passphrase, src, tarpath, decrypt=True)
    with tarfile.open(tarpath) as tar:
        tar.extractall(work, filter="data")
    os.unlink(tarpath)
    return work


def cmd_case_open(args):
    ensure_dirs()
    case_id = args.case_id
    if not valid_case_id(case_id):
        fail("invalid case id")
    cdir = case_dir(case_id)
    if not os.path.isdir(cdir):
        fail("unknown case: " + case_id)
    act = read_active()
    if act:
        fail("case %s is already open (close it first)" % act["case_id"])
    meta_path = os.path.join(cdir, "case.meta")
    meta = {}
    if os.path.exists(meta_path):
        try:
            meta = json.load(open(meta_path, encoding="utf-8"))
        except Exception:
            pass
    backend = meta.get("backend", "gocryptfs" if gocryptfs_available() else "bundle")
    passphrase = prompt_passphrase()

    if backend == "gocryptfs":
        vault = os.path.join(cdir, "vault")
        mnt = os.path.join(cdir, "mnt")
        if not os.path.isdir(vault):
            fail("case vault is missing")
        gocryptfs_mount(vault, mnt, passphrase)
        root = mnt
    else:
        root = unpack_workdir(cdir, passphrase)

    db = db_path(root)
    if not os.path.exists(db):
        if backend == "gocryptfs":
            gocryptfs_unmount(root)
        else:
            shutil.rmtree(root, ignore_errors=True)
        fail("case database missing or passphrase incorrect")
    try:
        conn = connect(db)
        conn.execute("SELECT 1 FROM cases LIMIT 1").fetchone()
        conn.close()
    except sqlite3.DatabaseError:
        fail("case database is unreadable (wrong passphrase?)")

    write_active({"case_id": case_id, "backend": backend, "root": root,
                  "opened_utc": now()})
    print("Opened %s (%s)" % (case_id, backend))
    print("Vault: %s" % root)
    print("Start the logged terminal with: bruma shell")


def cmd_case_close(args):
    act = read_active()
    if not act:
        fail("no open case")
    close_active(act, unmount=True)
    print("Closed %s" % act["case_id"])


def close_active(act, unmount=True, wipe=True):
    root = act.get("root", "")
    try:
        if act.get("backend") == "gocryptfs":
            if unmount:
                gocryptfs_unmount(root)
        else:
            cdir = case_dir(act["case_id"])
            if unmount:
                # Re-encrypt the working copy back into the case bundle.
                passphrase = prompt_passphrase()
                pack_workdir(cdir, root, passphrase)
            if wipe:
                shutil.rmtree(root, ignore_errors=True)
    finally:
        clear_active()


def cmd_case_status(args):
    act = read_active()
    if not act:
        print("No case is open.")
        return
    conn = connect(db_path(act["root"]))
    case = conn.execute("SELECT * FROM cases WHERE case_id=?", (act["case_id"],)).fetchone()
    st = chain_state(conn)
    arts = conn.execute("SELECT COUNT(*) c FROM artifacts WHERE case_id=?", (act["case_id"],)).fetchone()["c"]
    print("Case:     %s" % act["case_id"])
    if case:
        print("Title:    %s" % case["title"])
        print("Operator: %s" % case["operator"])
    print("Backend:  %s" % act["backend"])
    print("Vault:    %s" % act["root"])
    print("Events:   %d" % st["count"])
    print("Artifacts:%d" % arts)
    print("Root:     %s" % st["root"])
    print("Chain:    %s" % ("OK" if st["ok"] else "BROKEN"))
    for p in st["problems"]:
        print("  ! " + p)
    conn.close()


def cmd_case_list(args):
    ensure_dirs()
    ids = sorted(d for d in os.listdir(CASES_DIR) if os.path.isdir(os.path.join(CASES_DIR, d)))
    if not ids:
        print("No cases yet.")
        return
    act = read_active()
    for cid in ids:
        meta_path = os.path.join(CASES_DIR, cid, "case.meta")
        created = ""
        try:
            created = json.load(open(meta_path, encoding="utf-8")).get("created_utc", "")
        except Exception:
            pass
        mark = "*" if act and act["case_id"] == cid else " "
        print("%s %-40s %s" % (mark, cid, created))


# --------------------------------------------------------------------------
# evidence, notes, tool runs
# --------------------------------------------------------------------------
def add_artifact(conn, act, path, origin, source, notes, operator, host, etype="artifact"):
    st = os.stat(path)
    digest = sha256_file(path)
    mime = mimetypes.guess_type(path)[0] or ""
    eid, _ = add_event(conn, act["case_id"], etype, {
        "origin": origin, "source": source, "sha256": digest,
        "size": st.st_size, "mime": mime, "notes": notes}, operator, host)
    conn.execute(
        "INSERT INTO artifacts(case_id,path,origin,size,mime,sha256,first_seen,source,notes,event_id) "
        "VALUES(?,?,?,?,?,?,?,?,?,?)",
        (act["case_id"], path, origin, st.st_size, mime, digest, now(), source, notes, eid))
    conn.commit()
    return digest, eid


def cmd_evidence_add(args):
    act, db = require_active()
    conn = connect(db)
    operator, host = current_operator(), os.uname().nodename
    target = args.target
    if re.match(r"^https?://", target, re.I):
        try:
            with urllib.request.urlopen(target, timeout=20) as resp:
                data = resp.read(50 * 1024 * 1024)
        except Exception as exc:
            fail("cannot fetch URL: %s" % exc)
        arts = os.path.join(act["root"], "artifacts")
        os.makedirs(arts, mode=0o700, exist_ok=True)
        digest = sha256_bytes(data)
        name = re.sub(r"[^A-Za-z0-9._-]+", "_", target.split("://", 1)[1])[:80] or "url"
        dest = os.path.join(arts, digest[:16] + "-" + name)
        with open(dest, "wb") as fh:
            fh.write(data)
        add_artifact(conn, act, dest, "url", target, args.notes or "", operator, host)
        print("Registered URL evidence %s" % target)
        print("SHA-256: %s" % digest)
    else:
        src = os.path.abspath(os.path.expanduser(target))
        if not os.path.isfile(src):
            fail("not a file: " + target)
        arts = os.path.join(act["root"], "artifacts")
        os.makedirs(arts, mode=0o700, exist_ok=True)
        digest = sha256_file(src)
        dest = os.path.join(arts, digest[:16] + "-" + os.path.basename(src))
        shutil.copy2(src, dest)
        add_artifact(conn, act, dest, "file", src, args.notes or "", operator, host)
        print("Registered evidence %s" % src)
        print("SHA-256: %s" % digest)
    conn.close()


def cmd_note(args):
    act, db = require_active()
    text = " ".join(args.text).strip()
    if not text:
        fail("note text required")
    conn = connect(db)
    operator, host = current_operator(), os.uname().nodename
    eid, _ = add_event(conn, act["case_id"], "note", {"text": text}, operator, host)
    conn.execute("INSERT INTO notes(case_id,event_id,text,created_utc) VALUES(?,?,?,?)",
                 (act["case_id"], eid, text, now()))
    conn.commit()
    conn.close()
    print("Note recorded")


def log_command(conn, act, argv, exit_code, duration_ms, cwd, out_path, err_path):
    operator, host = current_operator(), os.uname().nodename
    out_sha = sha256_file(out_path) if out_path and os.path.exists(out_path) else ""
    err_sha = sha256_file(err_path) if err_path and os.path.exists(err_path) else ""
    payload = {"argv": argv, "exit_code": exit_code, "duration_ms": duration_ms,
               "cwd": cwd, "stdout_sha256": out_sha, "stderr_sha256": err_sha}
    eid, _ = add_event(conn, act["case_id"], "tool_run", payload, operator, host)
    conn.execute(
        "INSERT INTO tool_runs(case_id,event_id,argv,exit_code,duration_ms,cwd,"
        "stdout_path,stderr_path,stdout_sha256,stderr_sha256,started_utc,ended_utc) "
        "VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
        (act["case_id"], eid, json.dumps(argv), exit_code, duration_ms, cwd,
         out_path or "", err_path or "", out_sha, err_sha, now(), now()))
    conn.commit()
    for path, sha, label in ((out_path, out_sha, "stdout"), (err_path, err_sha, "stderr")):
        if path and os.path.exists(path):
            st = os.stat(path)
            conn.execute(
                "INSERT INTO artifacts(case_id,path,origin,size,mime,sha256,first_seen,source,notes,event_id) "
                "VALUES(?,?,?,?,?,?,?,?,?,?)",
                (act["case_id"], path, "tool_output", st.st_size, "text/plain", sha,
                 now(), "%s:%s" % (argv[0] if argv else "cmd", label), "", eid))
    conn.commit()
    return eid


def find_real_tool(name):
    clean = os.pathsep.join(p for p in os.environ.get("PATH", "").split(os.pathsep)
                            if ".bruma" not in p)
    return shutil.which(name, path=clean)


def cmd_run(args):
    act, db = require_active()
    argv = list(args.cmd)
    if argv and argv[0] == "--":
        argv = argv[1:]
    if not argv:
        fail("no command given")
    tool = args.tool
    real = None
    if tool:
        real = find_real_tool(tool)
        if not real:
            fail("tool not found: " + tool)
        argv = [real] + argv
    logs = os.path.join(act["root"], "logs")
    os.makedirs(logs, mode=0o700, exist_ok=True)
    eid = str(uuid.uuid4())
    out_path = os.path.join(logs, eid + ".out")
    err_path = os.path.join(logs, eid + ".err")
    started = time.time()
    try:
        proc = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        import threading
        def pump(stream, path, echo):
            with open(path, "w", encoding="utf-8", errors="replace") as fh:
                for line in stream:
                    fh.write(line)
                    echo.write(line)
                    echo.flush()
        t1 = threading.Thread(target=pump, args=(proc.stdout, out_path, sys.stdout))
        t2 = threading.Thread(target=pump, args=(proc.stderr, err_path, sys.stderr))
        t1.start(); t2.start()
        code = proc.wait()
        t1.join(); t2.join()
    except FileNotFoundError:
        fail("command not found: " + argv[0])
    duration = int((time.time() - started) * 1000)
    conn = connect(db)
    log_command(conn, act, argv, code, duration, os.getcwd(), out_path, err_path)
    conn.close()
    sys.exit(code)


def cmd_shell(args):
    act, db = require_active()
    root = act["root"]
    bindir = os.path.join(root, ".bruma", "bin")
    os.makedirs(bindir, mode=0o700, exist_ok=True)
    tools = ["maigret", "sherlock", "holehe", "blackbird", "h8mail", "nmap",
             "whois", "dig", "exiftool", "tshark", "wireshark-cli", "binwalk", "mat2"]
    for tool in tools:
        real = find_real_tool(tool)
        if not real:
            continue
        script = os.path.join(bindir, tool)
        with open(script, "w", encoding="utf-8") as fh:
            fh.write("#!/bin/sh\nexec bruma run --tool %s -- \"$@\"\n" % tool)
        os.chmod(script, 0o700)
    rc = os.path.join(root, ".bruma", "bashrc")
    with open(rc, "w", encoding="utf-8") as fh:
        fh.write("""# OpenBruma case shell
[ -f /etc/bash.bashrc ] && . /etc/bash.bashrc
[ -f "$HOME/.bashrc" ] && . "$HOME/.bashrc"
export BRUMA_CASE=%s
export PATH=%s:$PATH
export PS1='\\[\\e[38;2;0;255;157m\\](case %s)\\[\\e[0m\\] \\u@\\h:\\w\\n> '
__bruma_cmd=""
__bruma_t0=0
__bruma_inhook=0
__bruma_preexec() {
  [ "$__bruma_inhook" = "1" ] && return
  local c="$BASH_COMMAND"
  case "$c" in *__bruma_*|*bruma\\ shell*) return;; esac
  __bruma_cmd="$c"; __bruma_t0=$(date +%%s%%3N 2>/dev/null || echo 0)
}
__bruma_precmd() {
  local ec=$?
  [ "$__bruma_inhook" = "1" ] && return
  if [ -n "$__bruma_cmd" ]; then
    __bruma_inhook=1
    local t1=$(date +%%s%%3N 2>/dev/null || echo 0)
    %s _event command --cmd "$__bruma_cmd" --exit "$ec" --ms $((t1-__bruma_t0)) --cwd "$PWD" >/dev/null 2>&1
    __bruma_inhook=0
    __bruma_cmd=""
  fi
}
trap __bruma_preexec DEBUG
PROMPT_COMMAND=__bruma_precmd
echo "OpenBruma case %s - commands are recorded. Seal with: bruma case seal"
""" % (act["case_id"], bindir, act["case_id"],
       os.path.join(os.path.dirname(os.path.abspath(__file__)), "bruma"),
       act["case_id"]))
    transcripts = os.path.join(root, "transcripts")
    os.makedirs(transcripts, mode=0o700, exist_ok=True)
    logfile = os.path.join(transcripts, "session-" + datetime.now().strftime("%Y%m%d-%H%M%S") + ".log")
    cmd = ["bash", "--rcfile", rc, "-i"]
    if have("script"):
        cmd = ["script", "-q", "-f", logfile, "-c", "bash --rcfile '%s' -i" % rc]
    env = dict(os.environ)
    env["BRUMA_CASE"] = act["case_id"]
    env["PATH"] = bindir + os.pathsep + env.get("PATH", "")
    try:
        subprocess.call(cmd, env=env)
    finally:
        if os.path.exists(logfile) and os.path.getsize(logfile) > 0:
            conn = connect(db)
            add_artifact(conn, act, logfile, "transcript", "case shell", "", current_operator(),
                         os.uname().nodename, etype="transcript")
            conn.close()
            print("Transcript recorded: " + logfile)


def cmd_internal_event(args):
    act = read_active()
    if not act:
        return
    conn = connect(db_path(act["root"]))
    payload = {"command": args.cmd, "exit_code": args.exit, "duration_ms": args.ms,
               "cwd": args.cwd}
    add_event(conn, act["case_id"], "command", payload, current_operator(), os.uname().nodename)
    conn.close()


# --------------------------------------------------------------------------
# seal / verify / export
# --------------------------------------------------------------------------
def gather(conn, case_id):
    case = dict(conn.execute("SELECT * FROM cases WHERE case_id=?", (case_id,)).fetchone())
    events = [dict(r) for r in conn.execute(
        "SELECT seq,case_id,event_id,ts_utc,type,operator,host,payload,previous_hash,event_hash "
        "FROM events WHERE case_id=? ORDER BY seq", (case_id,))]
    artifacts = [dict(r) for r in conn.execute(
        "SELECT * FROM artifacts WHERE case_id=? ORDER BY id", (case_id,))]
    tool_runs = [dict(r) for r in conn.execute(
        "SELECT * FROM tool_runs WHERE case_id=? ORDER BY id", (case_id,))]
    notes = [dict(r) for r in conn.execute(
        "SELECT * FROM notes WHERE case_id=? ORDER BY id", (case_id,))]
    return case, events, artifacts, tool_runs, notes


def write_report(path, case, events, artifacts, root_hash, signature=""):
    def esc(value):
        return (str(value).replace("&", "&amp;").replace("<", "&lt;")
                .replace(">", "&gt;").replace('"', "&quot;"))
    rows = []
    for ev in events:
        payload = json.loads(ev["payload"])
        summary = payload.get("command") or payload.get("text") or payload.get("argv") \
            or payload.get("sha256") or payload.get("title") or ""
        if isinstance(summary, list):
            summary = " ".join(summary)
        rows.append("<tr><td>%s</td><td>%s</td><td>%s</td><td class='mono'>%s</td></tr>"
                    % (esc(ev["seq"]), esc(ev["ts_utc"]), esc(ev["type"]), esc(summary)[:600]))
    art_rows = []
    for a in artifacts:
        art_rows.append("<tr><td class='mono'>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>"
                        % (esc(a["sha256"]), esc(a["size"]), esc(a["mime"]),
                           esc(a["origin"] or a["source"])))
    html = """<!doctype html><html><head><meta charset="utf-8">
<title>OpenBruma case %s</title>
<style>
body{background:#0a0c0f;color:#dcecff;font-family:Inter,DejaVu Sans,sans-serif;margin:2em;}
h1,h2{color:#00ff9d} table{border-collapse:collapse;width:100%%;margin:1em 0}
td,th{border:1px solid #1b4a3a;padding:6px;font-size:90%%;vertical-align:top}
th{background:#0f1a1a;color:#00ff9d;text-align:left}
.mono{font-family:'Share Tech Mono',monospace;word-break:break-all}
.notice{border:1px solid #ffcc00;padding:10px;color:#ffcc00;margin:1em 0}
code{background:#0f1418;padding:2px 4px}
</style></head><body>
<h1>OpenBruma Case Capsule - case report</h1>
<p class="notice">%s</p>
<h2>Case</h2>
<table>
<tr><th>Case ID</th><td class="mono">%s</td></tr>
<tr><th>Title</th><td>%s</td></tr>
<tr><th>Operator</th><td>%s</td></tr>
<tr><th>Host</th><td>%s</td></tr>
<tr><th>Created (UTC)</th><td>%s</td></tr>
<tr><th>Sealed (UTC)</th><td>%s</td></tr>
<tr><th>Scope</th><td>%s</td></tr>
<tr><th>Events</th><td>%d</td></tr>
<tr><th>Artifacts</th><td>%d</td></tr>
<tr><th>Root hash</th><td class="mono">%s</td></tr>
<tr><th>Signature</th><td class="mono">%s</td></tr>
</table>
<h2>Chain-of-custody timeline</h2>
<table><tr><th>#</th><th>UTC</th><th>Type</th><th>Summary</th></tr>
%s
</table>
<h2>Artifacts</h2>
<table><tr><th>SHA-256</th><th>Size</th><th>MIME</th><th>Source</th></tr>
%s
</table>
<h2>Verification</h2>
<p>Each event hash is SHA-256 over the canonical JSON of the event plus the
previous event hash. The root hash is the last event hash. The bundle ships
<code>timeline.json</code>, <code>case.json</code> and <code>SHA256SUMS</code>.</p>
<pre>bruma case verify &lt;bundle&gt;</pre>
<p>Case Capsule produces tamper-evident documentation. It is not a certified
forensic tool and this report does not by itself establish legal admissibility.</p>
</body></html>""" % (esc(case["case_id"]), LEGAL, esc(case["case_id"]), esc(case["title"]),
                     esc(case["operator"]), esc(case["host"]), esc(case["created_utc"]),
                     esc(now()), esc(case.get("scope", "")), len(events), len(artifacts),
                     esc(root_hash), esc(signature or "none"), "\n".join(rows),
                     "\n".join(art_rows))
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(html)


def export_plain(conn, case_id, outdir, signature=""):
    case, events, artifacts, tool_runs, notes = gather(conn, case_id)
    st = chain_state(conn)
    root = st["root"]
    os.makedirs(outdir, mode=0o700, exist_ok=True)
    with open(os.path.join(outdir, "case.json"), "w", encoding="utf-8") as fh:
        json.dump({"case": case, "root_hash": root, "event_count": len(events),
                   "artifact_count": len(artifacts), "exported_utc": now(),
                   "version": VERSION, "legal": LEGAL, "signature": signature},
                  fh, indent=2)
    with open(os.path.join(outdir, "timeline.json"), "w", encoding="utf-8") as fh:
        json.dump(events, fh, indent=2)
    with open(os.path.join(outdir, "artifacts.json"), "w", encoding="utf-8") as fh:
        json.dump(artifacts, fh, indent=2)
    with open(os.path.join(outdir, "tool_runs.json"), "w", encoding="utf-8") as fh:
        json.dump(tool_runs, fh, indent=2)
    with open(os.path.join(outdir, "notes.json"), "w", encoding="utf-8") as fh:
        json.dump(notes, fh, indent=2)
    write_report(os.path.join(outdir, "report.html"), case, events, artifacts, root, signature)
    sums = []
    for name in ("case.json", "timeline.json", "artifacts.json", "tool_runs.json",
                 "notes.json", "report.html"):
        sums.append("%s  %s" % (sha256_file(os.path.join(outdir, name)), name))
    with open(os.path.join(outdir, "SHA256SUMS"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(sums) + "\n")
    return root, len(events), len(artifacts)


def gpg_secret_available():
    if not have("gpg"):
        return False
    res = subprocess.run(["gpg", "--batch", "--list-secret-keys", "--with-colons"],
                         capture_output=True, text=True)
    return res.returncode == 0 and "sec:" in res.stdout


def sign_sums(outdir):
    sums = os.path.join(outdir, "SHA256SUMS")
    if not gpg_secret_available():
        return ""
    res = subprocess.run(["gpg", "--batch", "--yes", "--armor", "--detach-sign",
                          "--output", sums + ".asc", sums], capture_output=True, text=True)
    if res.returncode != 0:
        return ""
    info = subprocess.run(["gpg", "--batch", "--list-keys", "--with-colons"],
                          capture_output=True, text=True)
    fpr = ""
    for line in info.stdout.splitlines():
        if line.startswith("fpr:"):
            fpr = line.split(":")[9]
            break
    return fpr or "signed"


def cmd_case_seal(args):
    act, db = require_active()
    conn = connect(db)
    st = chain_state(conn)
    if not st["ok"]:
        conn.close()
        fail("refusing to seal: hash chain is broken:\n  " + "\n  ".join(st["problems"]))
    case_id = act["case_id"]
    if args.notes:
        conn.execute("UPDATE cases SET notes=? WHERE case_id=?", (args.notes, case_id))
        conn.commit()
    add_event(conn, case_id, "case_sealed", {"root_before_seal": st["root"]},
              current_operator(), os.uname().nodename)
    conn.commit()
    st2 = chain_state(conn)
    if not st2["ok"]:
        conn.close()
        fail("refusing to seal: chain broke while sealing")
    passphrase = prompt_passphrase(confirm=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    plain = os.path.join(EXPORT_HOME, "plain-" + case_id + "-" + stamp)
    try:
        root, nevents, narts = export_plain(conn, case_id, plain)
        sig = sign_sums(plain)
        if sig:
            with open(os.path.join(plain, "SIGNATURE.txt"), "w", encoding="utf-8") as fh:
                fh.write("SHA256SUMS signed by %s\n" % sig)
            export_plain(conn, case_id, plain, sig)
        arts_src = os.path.join(act["root"], "artifacts")
        if os.path.isdir(arts_src):
            shutil.copytree(arts_src, os.path.join(plain, "artifacts"), dirs_exist_ok=True)
    finally:
        conn.close()
    tarpath = plain + ".tar.xz"
    with tarfile.open(tarpath, "w:xz") as tar:
        for name in os.listdir(plain):
            tar.add(os.path.join(plain, name), arcname=name)
    bundle = os.path.join(EXPORT_HOME, "%s-sealed-%s.tar.xz.%s"
                          % (case_id, stamp, "gpg" if preferred_backend() == "gpg" else "age"))
    encrypt_file(passphrase, tarpath, bundle, decrypt=False)
    os.unlink(tarpath)
    if not args.keep_plaintext:
        shutil.rmtree(plain, ignore_errors=True)
    # Record the seal inside the case before unmounting.
    if act["backend"] == "gocryptfs":
        conn = connect(db)
        conn.execute("INSERT INTO seals(case_id,sealed_utc,root_hash,event_count,artifact_count,bundle_path,signature) "
                     "VALUES(?,?,?,?,?,?,?)",
                     (case_id, now(), root, nevents, narts, bundle, sig or ""))
        conn.commit(); conn.close()
        close_active(act, unmount=True, wipe=False)
    else:
        close_active(act, unmount=True, wipe=True)
    print("Sealed case %s" % case_id)
    print("Events:   %d" % nevents)
    print("Artifacts:%d" % narts)
    print("Root:     %s" % root)
    if sig:
        print("Signed:   %s" % sig)
    print("Bundle:   %s" % bundle)


def verify_bundle(bundle, passphrase):
    tmp = tempfile.mkdtemp(prefix="bruma-verify-",
                           dir=os.environ.get("XDG_RUNTIME_DIR") or "/tmp")
    os.chmod(tmp, 0o700)
    try:
        tarpath = os.path.join(tmp, "bundle.tar.xz")
        if bundle.endswith(".age"):
            age_crypt(passphrase, bundle, tarpath, decrypt=True)
        else:
            gpg_crypt(passphrase, bundle, tarpath, decrypt=True)
        with tarfile.open(tarpath) as tar:
            tar.extractall(tmp, filter="data")
        os.unlink(tarpath)
        case_json = json.load(open(os.path.join(tmp, "case.json"), encoding="utf-8"))
        timeline = json.load(open(os.path.join(tmp, "timeline.json"), encoding="utf-8"))
        prev = CHAIN_START
        problems = []
        expected = 1
        for ev in timeline:
            if ev["seq"] != expected:
                problems.append("sequence gap at %s" % ev["seq"])
            expected = ev["seq"] + 1
            base = {k: ev[k] for k in ("case_id", "event_id", "ts_utc", "type",
                                       "operator", "host")}
            base["payload"] = json.loads(ev["payload"])
            digest = sha256_bytes((canonical(base) + prev).encode("utf-8"))
            if digest != ev["event_hash"]:
                problems.append("event %s hash mismatch" % ev["event_id"])
            if ev["previous_hash"] != prev:
                problems.append("event %s previous_hash mismatch" % ev["event_id"])
            prev = ev["event_hash"]
        if prev != case_json.get("root_hash"):
            problems.append("root hash does not match case.json")
        # artifact checksums (when the artifacts are included)
        artdir = os.path.join(tmp, "artifacts")
        if os.path.isdir(artdir):
            for name in os.listdir(artdir):
                p = os.path.join(artdir, name)
                if os.path.isfile(p):
                    digest = sha256_file(p)
                    if not any(a["sha256"] == digest for a in
                               json.load(open(os.path.join(tmp, "artifacts.json"), encoding="utf-8"))):
                        problems.append("artifact not registered: " + name)
        sums_ok = True
        sums_path = os.path.join(tmp, "SHA256SUMS")
        if os.path.exists(sums_path):
            for line in open(sums_path, encoding="utf-8"):
                line = line.strip()
                if not line:
                    continue
                digest, name = line.split(None, 1)
                target = os.path.join(tmp, name.strip())
                if os.path.exists(target) and sha256_file(target) != digest:
                    sums_ok = False
                    problems.append("checksum mismatch: " + name)
        ok = not problems
        print("Verify: %s" % ("PASS" if ok else "FAIL"))
        print("Case:   %s" % case_json.get("case", {}).get("case_id", "?"))
        print("Events: %d" % len(timeline))
        print("Root:   %s" % prev)
        if not sums_ok:
            print("SHA256SUMS: FAIL")
        for p in problems:
            print("  ! " + p)
        return 0 if ok else 2
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def cmd_case_verify(args):
    passphrase = prompt_passphrase()
    sys.exit(verify_bundle(args.bundle, passphrase))


def cmd_case_export(args):
    act = read_active()
    if not act:
        fail("open the case first (bruma case open <id>)")
    conn = connect(db_path(act["root"]))
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    outdir = os.path.join(EXPORT_HOME, "export-" + act["case_id"] + "-" + stamp)
    root, nevents, narts = export_plain(conn, act["case_id"], outdir, sign_sums(outdir))
    conn.close()
    print("Exported (plaintext, unsealed): %s" % outdir)
    print("Root: %s  events: %d  artifacts: %d" % (root, nevents, narts))


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------
def main(argv=None):
    parser = argparse.ArgumentParser(prog="bruma", description=APP + " " + VERSION)
    parser.add_argument("--version", action="version", version=VERSION)
    sub = parser.add_subparsers(dest="section")

    case = sub.add_parser("case", help="case lifecycle")
    csub = case.add_subparsers(dest="action")

    p = csub.add_parser("new", help="create a case")
    p.add_argument("title")
    p.add_argument("--operator")
    p.add_argument("--scope", default="")
    p.add_argument("--id")
    p.set_defaults(func=cmd_case_new)

    p = csub.add_parser("open", help="open (mount) a case")
    p.add_argument("case_id")
    p.set_defaults(func=cmd_case_open)

    p = csub.add_parser("close", help="close the active case")
    p.set_defaults(func=cmd_case_close)

    p = csub.add_parser("status", help="show active case status")
    p.set_defaults(func=cmd_case_status)

    p = csub.add_parser("list", help="list cases")
    p.set_defaults(func=cmd_case_list)

    p = csub.add_parser("seal", help="seal and export the active case")
    p.add_argument("--notes", default="")
    p.add_argument("--keep-plaintext", action="store_true")
    p.set_defaults(func=cmd_case_seal)

    p = csub.add_parser("verify", help="verify a sealed bundle")
    p.add_argument("bundle")
    p.set_defaults(func=cmd_case_verify)

    p = csub.add_parser("export", help="export the open case as plain files")
    p.add_argument("case_id")
    p.add_argument("--html", action="store_true")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_case_export)

    p = sub.add_parser("shell", help="logged case terminal")
    p.set_defaults(func=cmd_shell)

    p = sub.add_parser("run", help="run one command with capture")
    p.add_argument("--tool", default=None)
    p.add_argument("cmd", nargs=argparse.REMAINDER)
    p.set_defaults(func=cmd_run)

    p = sub.add_parser("note", help="add a note")
    p.add_argument("text", nargs="+")
    p.set_defaults(func=cmd_note)

    p = sub.add_parser("evidence", help="register evidence")
    esub = p.add_subparsers(dest="eaction")
    q = esub.add_parser("add")
    q.add_argument("target")
    q.add_argument("--notes", default="")
    q.set_defaults(func=cmd_evidence_add)

    p = sub.add_parser("_event", help=argparse.SUPPRESS)
    p.add_argument("kind")
    p.add_argument("--cmd", default="")
    p.add_argument("--exit", type=int, default=0)
    p.add_argument("--ms", type=int, default=0)
    p.add_argument("--cwd", default="")
    p.set_defaults(func=cmd_internal_event)

    args = parser.parse_args(argv)
    if not getattr(args, "func", None):
        parser.print_help()
        return 1
    args.func(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Copy qrbin .deb files into this apt repository and sign the index."""

from __future__ import annotations

import gzip
import hashlib
import io
import os
import shutil
import subprocess
import sys
import tarfile
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parent
GNUPG = ROOT / ".gnupg"
ARCHES = ("amd64", "arm64", "all")


def main() -> None:
    sources = [Path(arg).resolve() for arg in sys.argv[1:]]
    for source in sources:
        if not source.is_file():
            raise SystemExit(f"missing deb: {source}")
        place(source)
    debs = sorted((ROOT / "pool").rglob("*.deb"))
    if not debs:
        raise SystemExit("no .deb files in pool/. Pass the files from make deb.")
    records: dict[str, list[str]] = {arch: [] for arch in ARCHES}
    for deb in debs:
        arch, stanza = packages_stanza(deb)
        records[arch].append(stanza)
        print(f"index {deb.relative_to(ROOT)}")
    written = write_packages(records)
    write_release(written)
    fingerprint = ensure_key()
    sign(fingerprint)
    export_public_key()
    check_release()
    check_signature()
    grouped = " ".join(fingerprint[i : i + 4] for i in range(0, len(fingerprint), 4))
    print(f"signed dists/stable/InRelease")
    print(f"key {grouped}")


def place(source: Path) -> None:
    control = read_control(source.read_bytes())
    package = field(control, "Package")
    prefix = package[:4] if package.startswith("lib") else package[:1]
    dest = ROOT / "pool" / "main" / prefix / package / source.name
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.resolve() != source.resolve():
        shutil.copyfile(source, dest)
    print(f"pool {dest.relative_to(ROOT)}")


def packages_stanza(deb: Path) -> tuple[str, str]:
    data = deb.read_bytes()
    control = read_control(data)
    arch = field(control, "Architecture")
    if arch not in ARCHES:
        raise SystemExit(f"{deb.name} has architecture {arch}")
    hashes = [
        f"Installed-Size: {unpacked_kib(data)}",
        f"Filename: {deb.relative_to(ROOT).as_posix()}",
        f"Size: {len(data)}",
        f"MD5sum: {hashlib.md5(data).hexdigest()}",
        f"SHA1: {hashlib.sha1(data).hexdigest()}",
        f"SHA256: {hashlib.sha256(data).hexdigest()}",
    ]
    lines = control.strip("\n").split("\n")
    stanza: list[str] = []
    inserted = False
    for line in lines:
        if not inserted and line.startswith("Description:"):
            stanza.extend(hashes)
            inserted = True
        stanza.append(line)
    if not inserted:
        stanza.extend(hashes)
    return arch, "\n".join(stanza)


def write_packages(records: dict[str, list[str]]) -> list[tuple[str, bytes]]:
    written: list[tuple[str, bytes]] = []
    dist = ROOT / "dists" / "stable"
    for arch, stanzas in records.items():
        if not stanzas:
            continue
        body = ("\n\n".join(stanzas) + "\n").encode()
        folder = dist / "main" / f"binary-{arch}"
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "Packages").write_bytes(body)
        compressed = gzip.compress(body, mtime=0)
        (folder / "Packages.gz").write_bytes(compressed)
        base = f"main/binary-{arch}"
        written.append((f"{base}/Packages", body))
        written.append((f"{base}/Packages.gz", compressed))
    return written


def write_release(files: list[tuple[str, bytes]]) -> None:
    now = time.gmtime()
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    date = (
        f"{days[now.tm_wday]}, {now.tm_mday:02d} {months[now.tm_mon - 1]} {now.tm_year} "
        f"{now.tm_hour:02d}:{now.tm_min:02d}:{now.tm_sec:02d} UTC"
    )
    arches = sorted({path.split("/")[1].removeprefix("binary-") for path, _ in files})
    header = [
        "Origin: pesty-sh",
        "Label: pesty",
        "Suite: stable",
        "Codename: stable",
        f"Date: {date}",
        f"Architectures: {' '.join(arches)}",
        "Components: main",
        "Description: pesty-sh packages",
    ]
    ordered = sorted(files, key=lambda item: item[0])
    sections = [("MD5Sum", hashlib.md5), ("SHA1", hashlib.sha1), ("SHA256", hashlib.sha256)]
    lines = list(header)
    for title, algo in sections:
        lines.append(f"{title}:")
        for path, data in ordered:
            lines.append(f" {algo(data).hexdigest()} {len(data)} {path}")
    release = ROOT / "dists" / "stable" / "Release"
    release.write_bytes(("\n".join(lines) + "\n").encode())
    print(f"wrote {release.relative_to(ROOT)}")


def ensure_key() -> str:
    GNUPG.mkdir(mode=0o700, exist_ok=True)
    os.chmod(GNUPG, 0o700)
    found = secret_fingerprint()
    if found:
        return found
    script = (
        "Key-Type: RSA\n"
        "Key-Length: 4096\n"
        "Key-Usage: sign\n"
        "Name-Real: pesty-sh\n"
        "Name-Comment: apt archive\n"
        "Name-Email: pesty@pesty.sh\n"
        "Expire-Date: 0\n"
        "%no-protection\n"
        "%commit\n"
    )
    run(
        [
            gpg_bin(),
            "--homedir",
            str(GNUPG),
            "--batch",
            "--pinentry-mode",
            "loopback",
            "--gen-key",
        ],
        input_text=script,
    )
    found = secret_fingerprint()
    if not found:
        raise SystemExit("gpg did not create a signing key")
    return found


def secret_fingerprint() -> str | None:
    if not GNUPG.exists():
        return None
    result = run(
        [
            gpg_bin(),
            "--homedir",
            str(GNUPG),
            "--batch",
            "--with-colons",
            "--list-secret-keys",
        ],
        check=False,
    )
    if result.returncode != 0:
        return None
    lines = result.stdout.splitlines()
    for index, line in enumerate(lines):
        if not line.startswith("sec:"):
            continue
        for follow in lines[index + 1 :]:
            if follow.startswith("fpr:"):
                return follow.split(":")[9]
            if follow.startswith(("sec:", "ssb:")):
                break
    return None


def sign(fingerprint: str) -> None:
    dist = ROOT / "dists" / "stable"
    release = dist / "Release"
    common = [
        gpg_bin(),
        "--homedir",
        str(GNUPG),
        "--batch",
        "--yes",
        "--no-tty",
        "--pinentry-mode",
        "loopback",
        "--digest-algo",
        "SHA256",
        "--local-user",
        fingerprint,
    ]
    run(common + ["--clearsign", "--output", str(dist / "InRelease"), str(release)])
    run(common + ["--detach-sign", "--armor", "--output", str(dist / "Release.gpg"), str(release)])


def export_public_key() -> None:
    run(
        [
            gpg_bin(),
            "--homedir",
            str(GNUPG),
            "--batch",
            "--export",
            "--output",
            str(ROOT / "pesty-archive-keyring.gpg"),
        ]
    )
    run(
        [
            gpg_bin(),
            "--homedir",
            str(GNUPG),
            "--batch",
            "--armor",
            "--export",
            "--output",
            str(ROOT / "pesty-archive-keyring.asc"),
        ]
    )


def check_release() -> None:
    dist = ROOT / "dists" / "stable"
    text = (dist / "Release").read_text()
    section = None
    algos = {"MD5Sum": hashlib.md5, "SHA1": hashlib.sha1, "SHA256": hashlib.sha256}
    checked = 0
    for line in text.splitlines():
        if line.endswith(":") and line[:-1] in algos:
            section = line[:-1]
            continue
        if section is None or not line.startswith(" "):
            section = None
            continue
        digest, size, path = line[1:].split()
        data = (dist / path).read_bytes()
        if algos[section](data).hexdigest() != digest or str(len(data)) != size:
            raise SystemExit(f"Release hash does not match {path}")
        checked += 1
    if checked < 3:
        raise SystemExit("Release is missing package index hashes")


def check_signature() -> None:
    dist = ROOT / "dists" / "stable"
    run(
        [
            gpg_bin(),
            "--homedir",
            str(GNUPG),
            "--batch",
            "--verify",
            str(dist / "InRelease"),
        ]
    )
    run(
        [
            gpg_bin(),
            "--homedir",
            str(GNUPG),
            "--batch",
            "--verify",
            str(dist / "Release.gpg"),
            str(dist / "Release"),
        ]
    )


def gpg_bin() -> str:
    found = shutil.which("gpg")
    if found:
        return found
    candidates = [
        Path("/usr/local/bin/gpg"),
        Path.home() / ".cache" / "qrbin" / "gpg-bin" / "bin" / "gpg",
        Path.home() / ".cache" / "qrbin" / "gpg" / "bin" / "gpg",
    ]
    for candidate in candidates:
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return str(candidate)
    raise SystemExit("gpg is missing. A copy belongs at ~/.cache/qrbin/gpg-bin/bin/gpg.")


def run(args: list[str], input_text: str | None = None, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        args,
        input=input_text,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if check and result.returncode != 0:
        sys.stderr.write(result.stderr)
        raise SystemExit(f"command failed: {' '.join(args)}")
    return result


def read_control(deb: bytes) -> str:
    members = ar_members(deb)
    blob = members.get("control.tar.gz")
    if blob is None:
        raise SystemExit("deb is missing control.tar.gz")
    with tarfile.open(fileobj=io.BytesIO(blob), mode="r:gz") as archive:
        for member in archive.getmembers():
            if Path(member.name).name == "control" and member.isfile():
                extracted = archive.extractfile(member)
                if extracted is not None:
                    return extracted.read().decode()
    raise SystemExit("deb control archive has no control file")


def unpacked_kib(deb: bytes) -> int:
    blob = ar_members(deb).get("data.tar.gz")
    if blob is None:
        raise SystemExit("deb is missing data.tar.gz")
    total = 0
    with tarfile.open(fileobj=io.BytesIO(blob), mode="r:gz") as archive:
        for member in archive.getmembers():
            if member.isfile():
                total += member.size
    return (total + 1023) // 1024


def field(control: str, name: str) -> str:
    prefix = name + ":"
    for line in control.splitlines():
        if line.startswith(prefix):
            return line[len(prefix) :].strip()
    raise SystemExit(f"deb control is missing {name}")


def ar_members(data: bytes) -> dict[str, bytes]:
    if not data.startswith(b"!<arch>\n"):
        raise SystemExit("file is not a deb")
    members: dict[str, bytes] = {}
    pos = 8
    while pos + 60 <= len(data):
        header = data[pos : pos + 60]
        if header[58:60] != b"`\n":
            raise SystemExit("broken deb archive header")
        name = header[0:16].decode("ascii").strip().rstrip("/")
        size = int(header[48:58].decode("ascii").strip())
        pos += 60
        members[name] = data[pos : pos + size]
        pos += size + (size % 2)
    return members


if __name__ == "__main__":
    main()

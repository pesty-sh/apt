---
name: publish-apt
description: >-
  Sign and publish pesty-sh apt packages with the existing Mac GPG key.
  Use when the user asks to publish, sign, index, or push a .deb, run
  publish.py, update pesty-sh/apt or GitHub Pages, or mentions .gnupg,
  the apt fingerprint, qrbin, smashbin, or rmbin packaging.
---

# Publish the pesty-sh apt repository

Read this before running `publish.py`. qrbin was the first package signed. That run created the one key this repository still uses. smashbin and rmbin are later packages signed with that same key. There is no second key.

## Where signing is allowed

Signing happens only on Stuart's Mac, in this checkout:

`/Users/developers/Projects/pesty-sh/apt`

The private key is `.gnupg` in that directory. It is not in git. It is not on a cloud agent, a Linux VM, or any other computer. `gpg` on PATH is used, or `~/.cache/qrbin/gpg-bin/bin/gpg` when that file exists.

The secret key fingerprint must be exactly:

`2564 D17C 2F8B EC6A 9E59 6BB0 2B0D 9ACE 648D D6FF`

Raw form, as GnuPG prints it: `2564D17C2F8BEC6A9E596BB02B0D9ACE648DD6FF`

Public half, already in the repo: `pesty-archive-keyring.gpg` and `pesty-archive-keyring.asc`. Apt clients trust this fingerprint. A different key makes `apt-get update` fail.

## Stop before you create a key

`publish.py` calls `ensure_key()`. If `.gnupg` has no secret key, that function generates a new RSA key. That key is the wrong key. Do not let it run.

Stop, and do not run `publish.py`, when any of these are true:

- The current machine is not that Mac, or the working directory is not `/Users/developers/Projects/pesty-sh/apt`.
- `.gnupg` is missing. Do not create it. Do not run `gpg --homedir .gnupg` either: GnuPG creates an empty homedir, and the next `publish.py` would then generate a key.
- `gpg --homedir .gnupg --list-secret-keys --with-colons` has no `fpr` line, or the fingerprint is not `2564D17C2F8BEC6A9E596BB02B0D9ACE648DD6FF`.

Say that the key is missing and that the commands below have to be typed on the Mac. Do not download the `.deb` files "so they are ready". Do not commit `pool/` or `dists/` from this machine.

A cloud agent cannot publish this repository. Hand Stuart the commands. Do not improvise a new key "so the publish succeeds".

## Which files to sign

| Package | Where the `.deb` comes from | Architectures |
|---|---|---|
| qrbin | `make deb` in `/Users/developers/Projects/pesty-sh/rust/qrbin` | `amd64`, `arm64` |
| smashbin | `make deb` in `/Users/developers/Projects/pesty-sh/rust/smashbin` | `amd64`, `arm64` |
| rmbin | the files on the GitHub Release, not a local `make deb` | `amd64`, `arm64`, `armhf`, `i386` |

qrbin and smashbin in this pool are glibc builds from `make deb`. Do not replace them with the musl `.deb` files from a GitHub Release. Those are different binaries with the same filename.

rmbin is the other way round. Its release assets are the packages to publish. They are gzip members (`control.tar.gz`, `data.tar.gz`) and do not depend on `libc6`.

`publish.py` accepts Debian names `amd64`, `arm64`, `armhf`, `i386`, and `all`. Rust targets `armv7` and `i686` are refused. The `.deb` must say `armhf` and `i386`. An architecture with no package is left out of `dists/stable/Release`. After rmbin is in `pool/`, later publishes keep `armhf` and `i386`, because the script indexes every `.deb` already in `pool/`.

Leave older `.deb` files in `pool/`. Apt installs the newest version.

## On the Mac

Work on `main` in `/Users/developers/Projects/pesty-sh/apt`.

1. `git pull`
2. Confirm `.gnupg` is already there, then:

```bash
gpg --homedir .gnupg --list-secret-keys --with-colons
```

Stop if the fingerprint is missing or different.

3. If `git log -1` already uses the publish message for this version and the branch is ahead of `origin/main`, skip the download and `publish.py`. `git push` only.
4. Otherwise pass the `.deb` paths to `publish.py`. Write each filename in full. Do not build the name with a shell variable. A good run prints a `pool` line and an `index` line for every file, then `signed dists/stable/InRelease` and the fingerprint above.
5. Open `dists/stable/Release`. The `Architectures` line must list every architecture you just added, sorted, together with the architectures already in `pool/`.
6. Commit the index and the public key only:

```bash
git add pool dists pesty-archive-keyring.gpg pesty-archive-keyring.asc
```

Do not `git add .gnupg`. Author and committer are `stuarteske <sdeske@googlemail.com>`.

```bash
git commit -m "Publish <package> <version>."
git push
```

7. Report the pushed commit SHA.

GitHub Pages serves `main` at `https://pesty-sh.github.io/apt`. `.nojekyll` stays in the root. After the push, `apt-cache policy <package>` on a machine that already has the source line shows the new version. Until that push, the install command cannot see the package.

## rmbin 0.0.1

This version is not in `pool/` until the Mac push. Download with these URLs, then publish all four in one run. One missing file leaves that architecture out of `Release`.

```bash
mkdir -p /tmp/rmbin-0.0.1
cd /tmp/rmbin-0.0.1
curl -fsSL -O https://github.com/pesty-sh/rmbin/releases/download/v0.0.1/rmbin_0.0.1-1_amd64.deb
curl -fsSL -O https://github.com/pesty-sh/rmbin/releases/download/v0.0.1/rmbin_0.0.1-1_arm64.deb
curl -fsSL -O https://github.com/pesty-sh/rmbin/releases/download/v0.0.1/rmbin_0.0.1-1_armhf.deb
curl -fsSL -O https://github.com/pesty-sh/rmbin/releases/download/v0.0.1/rmbin_0.0.1-1_i386.deb
ls -la
```

Stop if any file is missing or only a few kilobytes. A small file is an error page, not a package.

```bash
cd /Users/developers/Projects/pesty-sh/apt
python3 publish.py \
  /tmp/rmbin-0.0.1/rmbin_0.0.1-1_amd64.deb \
  /tmp/rmbin-0.0.1/rmbin_0.0.1-1_arm64.deb \
  /tmp/rmbin-0.0.1/rmbin_0.0.1-1_armhf.deb \
  /tmp/rmbin-0.0.1/rmbin_0.0.1-1_i386.deb
```

`dists/stable/Release` must contain:

```text
Architectures: amd64 arm64 armhf i386
```

`binary-armhf/Packages` and `binary-i386/Packages` name `Package: rmbin` and `Version: 0.0.1-1`. `binary-amd64/Packages` still names qrbin and smashbin.

```bash
git add pool dists pesty-archive-keyring.gpg pesty-archive-keyring.asc
git commit -m "Publish rmbin 0.0.1."
git push
```

If `git log -1` already says `Publish rmbin 0.0.1.` and the branch is ahead of `origin/main`, skip the download and `publish.py`. Push.

## Do not

- Generate a signing key, copy `.gnupg` off the Mac, or commit `.gnupg`.
- Run `publish.py` against the real `pool/` or `dists/` on any machine except that Mac.
- Treat an empty `.gnupg` as "the key will be created on first publish". The key already exists. A new one is a different publisher.
- Sign qrbin or smashbin from their GitHub Release musl archives.
- Force-push `main`.

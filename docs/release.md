# Publish a package

Installing the programs is the [README](../README.md). The first-time walkthrough is [apt.md](apt.md). This page is for the Mac that publishes a new `.deb`.

Work in `/Users/developers/Projects/pesty-sh/apt`. The branch is `main`. The signing key stays in `.gnupg` on this Mac. `publish.py` is run here, and nowhere else.

Three packages share this repository:

| Package | Built from | Version in the index | Architectures |
|---|---|---|---|
| qrbin | `/Users/developers/Projects/pesty-sh/rust/qrbin` | `0.1.9-1` | `amd64`, `arm64` |
| smashbin | `/Users/developers/Projects/pesty-sh/rust/smashbin` | `0.1.5-1` | `amd64`, `arm64` |
| rmbin | the [v0.0.1 GitHub Release](https://github.com/pesty-sh/rmbin/releases/tag/v0.0.1) | `0.0.1-1` | `amd64`, `arm64`, `armhf`, `i386` |

`publish.py` accepts those four architectures, plus `all` (a package that is the same on every machine). The names are Debian architecture names, not Rust target triples. `armv7` in a Rust target is `armhf` inside the `.deb`. `i686` is `i386`. A `.deb` with any other Architecture is refused before `Release` is rewritten, so the previous signed index stays as it was. The refused file has already been copied into `pool/`. Move that file out of `pool/` before running `publish.py` again, or the next run stops on the same file.

Each architecture that has at least one package in `pool/` gets `dists/stable/main/binary-<arch>/Packages` and `Packages.gz`. The `Architectures` line in `dists/stable/Release` lists those names, sorted. An architecture with no package is omitted. A repository that only contains qrbin still says `amd64 arm64`. After rmbin is in `pool/`, later runs keep `armhf` and `i386` in that line, because the script indexes every `.deb` already in `pool/`, not only the files named on the command line.

## qrbin

From `/Users/developers/Projects/pesty-sh/rust/qrbin`:

* `make deb`

That writes `dist/qrbin_<version>-1_amd64.deb` and `dist/qrbin_<version>-1_arm64.deb`.

## smashbin

From `/Users/developers/Projects/pesty-sh/rust/smashbin`:

* `make deb`

That writes `dist/smashbin_<version>-1_amd64.deb` and `dist/smashbin_<version>-1_arm64.deb`. Pass those two files to `publish.py` the same way as qrbin.

## Index and sign

From this project, pass the `.deb` files to `publish.py`. The first run creates the signing key in `.gnupg`. The key has no passphrase, so the script can sign. Back up `.gnupg` after the first run.

`publish.py` uses `gpg` on `PATH`, or `~/.cache/qrbin/gpg-bin/bin/gpg` when that file exists. Homebrew on this Mac would compile GnuPG from source. The cached copy is the one to use.

Fingerprint: `2564 D17C 2F8B EC6A 9E59 6BB0 2B0D 9ACE 648D D6FF`

qrbin, as an example:

* `python3 publish.py /Users/developers/Projects/pesty-sh/rust/qrbin/dist/qrbin_0.1.9-1_amd64.deb /Users/developers/Projects/pesty-sh/rust/qrbin/dist/qrbin_0.1.9-1_arm64.deb`

`publish.py` copies each file into `pool/main/`, rewrites `dists/stable`, and signs `Release`. The pool folder is the first letter of the package name: `pool/main/q/qrbin/`, `pool/main/s/smashbin/`, `pool/main/r/rmbin/`. Running the script again with no arguments rewrites the index from whatever is already in `pool/`. Leave older debs in `pool/` so the index still lists them. Apt installs the newest version.

The package version is the version from `Cargo.toml` plus the Debian revision `-1`.

Commit `pool/`, `dists/`, and the public key. Leave `.gnupg` untracked.

* `git add pool dists pesty-archive-keyring.gpg pesty-archive-keyring.asc`
* `git commit -m "Publish qrbin <version>."`
* `git push`

## rmbin 0.0.1

rmbin's four `.deb` files are already built. They are the assets on the v0.0.1 release, not a `make deb` tree on this Mac. Each one is gzip-compressed (`control.tar.gz` and `data.tar.gz`), which is the layout `publish.py` reads. They do not depend on `libc6`.

Download them, then index all four in one run. One missing file would leave that architecture out of `Release`.

```bash
mkdir -p /tmp/rmbin-0.0.1
cd /tmp/rmbin-0.0.1
curl -fsSL -O https://github.com/pesty-sh/rmbin/releases/download/v0.0.1/rmbin_0.0.1-1_amd64.deb
curl -fsSL -O https://github.com/pesty-sh/rmbin/releases/download/v0.0.1/rmbin_0.0.1-1_arm64.deb
curl -fsSL -O https://github.com/pesty-sh/rmbin/releases/download/v0.0.1/rmbin_0.0.1-1_armhf.deb
curl -fsSL -O https://github.com/pesty-sh/rmbin/releases/download/v0.0.1/rmbin_0.0.1-1_i386.deb
```

From the apt repository:

```bash
cd /Users/developers/Projects/pesty-sh/apt
python3 publish.py \
  /tmp/rmbin-0.0.1/rmbin_0.0.1-1_amd64.deb \
  /tmp/rmbin-0.0.1/rmbin_0.0.1-1_arm64.deb \
  /tmp/rmbin-0.0.1/rmbin_0.0.1-1_armhf.deb \
  /tmp/rmbin-0.0.1/rmbin_0.0.1-1_i386.deb
```

A successful run prints a `pool` line and an `index` line for each file, including `pool/main/r/rmbin/rmbin_0.0.1-1_armhf.deb` and `pool/main/r/rmbin/rmbin_0.0.1-1_i386.deb`. It then writes `dists/stable/Release`. With qrbin and smashbin already in `pool/`, the architectures line is:

```text
Architectures: amd64 arm64 armhf i386
```

`all` is not in that line, because none of these packages use Architecture `all`.

Check the four new indexes exist:

```bash
ls dists/stable/main/binary-amd64/Packages \
  dists/stable/main/binary-arm64/Packages \
  dists/stable/main/binary-armhf/Packages \
  dists/stable/main/binary-i386/Packages
```

`binary-armhf/Packages` and `binary-i386/Packages` should name `Package: rmbin` and `Version: 0.0.1-1`. `binary-amd64/Packages` should still name qrbin and smashbin as well as rmbin.

Commit and push the same paths as the other packages:

```bash
git add pool dists pesty-archive-keyring.gpg pesty-archive-keyring.asc
git commit -m "Publish rmbin 0.0.1."
git push
```

## Serve it

GitHub Pages serves this repository from the `main` branch at `https://pesty-sh.github.io/apt`. `.nojekyll` is in the root so Pages publishes the debs and the index as files.

The install commands are in the README. On a Linux machine that already has the source line:

* `sudo apt-get update`
* `sudo apt-get install qrbin`
* `sudo apt-get install smashbin`
* `sudo apt-get install rmbin`

After the rmbin push, `apt-cache policy rmbin` shows candidate `0.0.1-1`. On an `armhf` or `i386` machine that candidate is the matching `.deb`. qrbin and smashbin stay `amd64` and `arm64` only.

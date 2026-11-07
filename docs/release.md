# Publish a package

Installing qrbin is the [README](../README.md). The first-time walkthrough is [apt.md](apt.md). This page is for the Mac that publishes a new `.deb`.

Work in `/Users/developers/Projects/pesty-sh/apt`. The branch is `main`.

The qrbin repo builds the packages. This repo publishes them. `make deb` does not install the Linux binary on the Mac, and this repo does not keep a second copy of the qrbin source.

## Build

From `/Users/developers/Projects/pesty-sh/rust/qrbin`:

* `make deb`

That writes `dist/qrbin_<version>-1_amd64.deb` and `dist/qrbin_<version>-1_arm64.deb`.

## Index and sign

From this project, pass those two files to `publish.py`. The first run creates the signing key in `.gnupg`. The key has no passphrase, so the script can sign. Back up `.gnupg` after the first run.

`publish.py` uses `gpg` on `PATH`, or `~/.cache/qrbin/gpg-bin/bin/gpg` when that file exists. Homebrew on this Mac would compile GnuPG from source. The cached copy is the one to use.

Fingerprint: `2564 D17C 2F8B EC6A 9E59 6BB0 2B0D 9ACE 648D D6FF`

* `python3 publish.py /Users/developers/Projects/pesty-sh/rust/qrbin/dist/qrbin_0.1.9-1_amd64.deb /Users/developers/Projects/pesty-sh/rust/qrbin/dist/qrbin_0.1.9-1_arm64.deb`

`publish.py` copies each file into `pool/main/`, rewrites `dists/stable`, and signs `Release`. Running it again with no arguments rewrites the index from whatever is already in `pool/`.

The package version is the version from `Cargo.toml` plus the Debian revision `-1`. The next qrbin version is a new pair of debs. Leave older debs in `pool/` so the index still lists them. Apt installs the newest version.

Commit `pool/`, `dists/`, and `pesty-archive-keyring.gpg`. Leave `.gnupg` untracked.

* `git add pool dists pesty-archive-keyring.gpg pesty-archive-keyring.asc`
* `git commit -m "Publish qrbin <version>."`
* `git push`

## Serve it

GitHub Pages serves this repository from the `main` branch at `https://pesty-sh.github.io/apt`. `.nojekyll` is in the root so Pages publishes the debs and the index as files.

The install commands are in the README. On a Linux machine that already has the source line:

* `sudo apt-get update`
* `sudo apt-get install qrbin`

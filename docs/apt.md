# Apt, from the first command

This is the install guide for someone who has not used `apt-get` before. The repository holds three programs. None of them contact the network while they run.

| Package | What it does | Version | Architectures |
|---|---|---|---|
| [qrbin](https://github.com/pesty-sh/qrbin) | Turns text into a QR code image. | `0.1.9-1` | `amd64`, `arm64` |
| [smashbin](https://github.com/pesty-sh/smashbin) | Strips metadata and shrinks a PNG, JPG, or GIF. | `0.1.5-1` | `amd64`, `arm64` |
| [rmbin](https://github.com/pesty-sh/rmbin) | Overwrites a file you name with a repeating text pattern, syncs that write to disk, then deletes the file. | `0.0.1-1` | `amd64`, `arm64`, `armhf`, `i386` |

The walkthrough below installs qrbin, then uses the same repository for smashbin and rmbin. You do this on an Ubuntu or Debian computer. On a Mac, the install is Homebrew: `brew install pesty-sh/tap/qrbin`, `brew install pesty-sh/tap/smashbin`, or `brew install pesty-sh/tap/rmbin`.

rmbin permanently deletes the paths you give it. There is no warranty, and the authors accept no liability for lost files. Installing or removing the package only adds or removes `/usr/bin/rmbin`. It does not delete your files. Overwriting is best effort on SSDs, copy-on-write filesystems, snapshots, and backups. Read the [disclaimer](https://github.com/pesty-sh/rmbin/blob/v0.0.1/DISCLAIMER.md) before you point rmbin at a real file.

The short list of commands is on the [front page](../README.md). This page explains what each one does, how to check the computer you are on, and what the usual messages mean.

## The words

You will see these words in the commands and in apt's output.

| Word | Meaning |
|---|---|
| Package | A named program apt can install. The names here are `qrbin`, `smashbin`, and `rmbin`. |
| `.deb` | The file apt downloads. It holds the program and a short description. |
| Repository | A website with a package list and the `.deb` files. This one is `https://pesty-sh.github.io/apt`. |
| `apt-get` | The command that reads the list, downloads a package, and unpacks it. `apt` is the same tool with a slightly shorter prompt. Both work. The commands below use `apt-get`. |
| `sudo` | Runs the command as the administrator. Apt needs it because the program is installed for every user on the computer. |
| Source list | A text file that tells apt which repositories exist. Yours will be `/etc/apt/sources.list.d/pesty.list`. |
| Key | A small file apt uses to check the signature on the package list. You save it once. |
| Suite | The channel name inside the repository. Ours is `stable`. |
| Component | The section inside the suite. Ours is `main`. |
| Architecture | The kind of processor. `amd64` is 64-bit Intel and AMD. `arm64` is 64-bit ARM. `armhf` is 32-bit ARM. `i386` is 32-bit Intel and AMD. |

`0.1.9-1` is a package version. `0.1.9` is the program version. `-1` means the first time that version was packed into a `.deb`. smashbin is `0.1.5-1`. rmbin is `0.0.1-1`.

## Check the computer

Open a terminal. On Ubuntu, Ctrl+Alt+T opens one. The commands below are typed at the `$` prompt. You do not type the `$`.

See the system name and version:

```bash
cat /etc/os-release
```

Look at `VERSION_ID` and `ID`. These are the ones this repository supports:

| `ID` | `VERSION_ID` |
|---|---|
| `ubuntu` | `18.04`, `20.04`, `22.04`, `24.04` |
| `debian` | `10`, `11`, `12`, `13` |

See the processor apt will ask for:

```bash
dpkg --print-architecture
```

Apt matches that word to the package by itself when you install.

| `dpkg --print-architecture` | Packages you can install |
|---|---|
| `amd64` | qrbin, smashbin, rmbin |
| `arm64` | qrbin, smashbin, rmbin |
| `armhf` | rmbin |
| `i386` | rmbin |

qrbin and smashbin are not built for `armhf` or `i386`. On those machines `apt-get install qrbin` cannot find a package, and rmbin can.

You also need a network connection for the install. The programs do not use the network after that. The download is a few megabytes. rmbin's package does not depend on `libc6`. qrbin and smashbin need `libc6` 2.27 or newer, which the Ubuntu and Debian releases in the table already include.

## 1. Save the key

Apt will not use a repository until it can check a signature. The public key is safe to download. The private half stays on the Mac that publishes qrbin, smashbin, and rmbin.

```bash
sudo mkdir -p /usr/share/keyrings
curl -fsSL https://pesty-sh.github.io/apt/pesty-archive-keyring.gpg \
  | sudo tee /usr/share/keyrings/pesty-archive-keyring.gpg >/dev/null
```

Read it as three steps:

1. `sudo mkdir -p /usr/share/keyrings` creates the folder apt uses for repository keys, if the folder is not already there.
2. `curl` downloads the key from this site. `-fsSL` means: fail on an error, stay quiet, and follow a redirect.
3. `sudo tee` writes that download to `/usr/share/keyrings/pesty-archive-keyring.gpg`. `>/dev/null` hides the binary key from the terminal so you do not see garbage characters.

`sudo` asks for your password the first time. The characters do not appear as you type. Press Enter after the password.

The fingerprint of the key you just saved is:

`2564 D17C 2F8B EC6A 9E59 6BB0 2B0D 9ACE 648D D6FF`

To print the fingerprint of the file on disk:

```bash
gpg --show-keys --with-colons /usr/share/keyrings/pesty-archive-keyring.gpg
```

On a machine without `gpg`, skip that check. The install still works, because apt checks the signature itself during `apt-get update`.

## 2. Add the repository

```bash
echo "deb [signed-by=/usr/share/keyrings/pesty-archive-keyring.gpg] https://pesty-sh.github.io/apt stable main" \
  | sudo tee /etc/apt/sources.list.d/pesty.list
```

That one line is the whole configuration. The pieces are:

| Piece | What it tells apt |
|---|---|
| `deb` | Download installable packages. |
| `signed-by=...` | Accept signatures made by the key you saved in step 1, and by no other key. |
| `https://pesty-sh.github.io/apt` | The repository address. |
| `stable` | The channel. One channel covers every Ubuntu and Debian release in the table above. |
| `main` | The section. qrbin, smashbin, and rmbin are published in `main`. |

`tee` also prints the line in the terminal. That copy is the file apt will read. You can show it again any time:

```bash
cat /etc/apt/sources.list.d/pesty.list
```

## 3. Download the package list

```bash
sudo apt-get update
```

`update` does not install qrbin yet. It downloads the index and checks the signature.

A successful run mentions this repository and ends with a line like:

```text
Reading package lists... Done
```

You may also see a notice that a `Translation` file was not found. This repository publishes the package list in English inside the package itself, and it does not publish separate translation indexes. `update` still succeeded when the last line says the package lists were done.

Ask apt what it learned about qrbin:

```bash
apt-cache policy qrbin
```

A good answer includes `https://pesty-sh.github.io/apt` and a candidate version of `0.1.9-1`. The candidate is the version `install` will use.

`apt-cache show qrbin` prints the description from the package: a minimal offline QR code generator, depending on `libc6` version 2.27 or newer. That library is already part of the Ubuntu and Debian releases in the table.

`apt-cache policy smashbin` and `apt-cache policy rmbin` are the same check for the other two packages. smashbin's candidate version is `0.1.5-1`. rmbin's is `0.0.1-1`. A policy that does not mention `pesty-sh.github.io` means apt has not loaded this repository yet. If rmbin is missing while qrbin is listed, the rmbin packages have not been published into the repository yet. Publishing is [release.md](release.md).

## 4. Install

```bash
sudo apt-get install qrbin
```

Apt prints the package name, the version, and the download size, then asks:

```text
Do you want to continue? [Y/n]
```

Press Enter. `Y` is the default. Apt downloads `qrbin_0.1.9-1_amd64.deb` or `qrbin_0.1.9-1_arm64.deb`, unpacks it, and puts the program at `/usr/bin/qrbin`.

Confirm the install:

```bash
qrbin --version
command -v qrbin
```

`command -v` prints `/usr/bin/qrbin`. You can run `qrbin` from any directory because `/usr/bin` is on the default `PATH`.

Make one image:

```bash
qrbin hello > hello.png
```

`hello` is the text inside the QR code. `>` writes the image to a file named `hello.png` in the current directory. Open that file. A phone camera should read the word hello from it.

`qrbin --help` lists the options. The image goes to the terminal's output, so keep the `>` file redirect when you want a PNG on disk.

The same repository installs the other two packages. Repeat `sudo apt-get install` with the other name. You do not repeat steps 1 and 2.

smashbin:

```bash
sudo apt-get install smashbin
smashbin --version
command -v smashbin
```

`smashbin --version` prints `smashbin 0.1.5`. Apt downloads `smashbin_0.1.5-1_amd64.deb` or `smashbin_0.1.5-1_arm64.deb`.

rmbin:

```bash
sudo apt-get install rmbin
rmbin --version
command -v rmbin
```

`rmbin --version` prints `rmbin 0.0.1`. Apt downloads `rmbin_0.0.1-1_amd64.deb`, `rmbin_0.0.1-1_arm64.deb`, `rmbin_0.0.1-1_armhf.deb`, or `rmbin_0.0.1-1_i386.deb`, matching the architecture from `dpkg --print-architecture`.

This dry run does not delete the file. It prints what rmbin would do. Installing the package did not delete anything either.

```bash
printf 'hello\n' > /tmp/rmbin-example.txt
rmbin --dry-run /tmp/rmbin-example.txt
```

Stop there unless you have read the [disclaimer](https://github.com/pesty-sh/rmbin/blob/v0.0.1/DISCLAIMER.md) and you mean to destroy a file. There is no warranty.

## Upgrade

When a newer package is published, the source line stays as it is. Refresh the list, then install again:

```bash
sudo apt-get update
sudo apt-get install qrbin
```

If the machine already has the newest published version, apt says the package is already the newest version and leaves the file in place. Use `smashbin` or `rmbin` in place of `qrbin` to upgrade that package on its own.

`sudo apt-get upgrade` upgrades every installed package that has a newer version in any of your repositories, including these three.

## Remove

Remove the program and keep the configuration apt stored for it:

```bash
sudo apt-get remove qrbin
```

Remove the program and that stored configuration:

```bash
sudo apt-get purge qrbin
```

The same two commands work with `smashbin` or `rmbin` in place of `qrbin`. The repository line remains, so a later `sudo apt-get install qrbin` works without repeating steps 1 and 2. To stop apt from looking at this repository, delete the list file and refresh:

```bash
sudo rm /etc/apt/sources.list.d/pesty.list
sudo apt-get update
```

The key file can stay in `/usr/share/keyrings`. It is unused once the list file is gone.

## When a command fails

Read the last lines apt printed. These are the ones people hit on a first install.

**`Could not get lock` / `Unable to acquire the dpkg frontend lock`.** Another apt command is still running, often a software updater in the background. Wait for it to finish. Then run the command again.

**`Unable to locate package qrbin`.** The same message with `smashbin` or `rmbin` has the same cause: apt does not have this repository in its list yet, or that package is not published for your architecture. qrbin and smashbin exist for `amd64` and `arm64` only. rmbin also exists for `armhf` and `i386`. Check the file:

```bash
cat /etc/apt/sources.list.d/pesty.list
```

The line should match step 2 exactly. Then run `sudo apt-get update` again, and `apt-cache policy qrbin` (or `smashbin`, or `rmbin`). The policy output has to mention `pesty-sh.github.io` before `install` can find the package. If qrbin is listed and rmbin is not, the rmbin `.deb` files are not in the published index yet. That step is [release.md](release.md), done on the Mac that holds the signing key.

**`The following signatures couldn't be verified` or `NO_PUBKEY`.** The key file is missing or the `signed-by` path does not match it. Repeat step 1, then `sudo apt-get update`.

**`404 Not Found` for `InRelease`.** Apt could not download the signed index. Check the address in the list file. It is `https://pesty-sh.github.io/apt` with no extra path and no trailing slash required. A 404 on `Translation-en` alone is the notice described in step 3.

**`Temporary failure resolving` or `Could not resolve host`.** The computer could not look up the name. Check the network, then run `sudo apt-get update` again.

**`sudo: command not found`.** You are on a system image without `sudo`. Log in as root and run the same commands without `sudo`.

**`curl: command not found`.** Install curl from Ubuntu's own archive, which is already configured:

```bash
sudo apt-get update
sudo apt-get install curl
```

Then go back to step 1.

**`dpkg was interrupted`.** Finish the half-done install:

```bash
sudo dpkg --configure -a
sudo apt-get install qrbin
```

## What apt downloaded

The repository is a set of ordinary files. You can open `https://pesty-sh.github.io/apt` in a browser.

| File | Role |
|---|---|
| `pesty-archive-keyring.gpg` | The public key from step 1. |
| `dists/stable/InRelease` | The signed index. `apt-get update` downloads this first and checks the signature. |
| `dists/stable/main/binary-amd64/Packages` | 64-bit Intel and AMD packages: qrbin, smashbin, and rmbin. |
| `dists/stable/main/binary-arm64/Packages` | 64-bit ARM packages: qrbin, smashbin, and rmbin. |
| `dists/stable/main/binary-armhf/Packages` | 32-bit ARM packages. rmbin. This file is written when an `armhf` package is in the pool. |
| `dists/stable/main/binary-i386/Packages` | 32-bit Intel and AMD packages. rmbin. This file is written when an `i386` package is in the pool. |
| `pool/main/q/qrbin/qrbin_0.1.9-1_amd64.deb` | qrbin for 64-bit Intel and AMD. |
| `pool/main/q/qrbin/qrbin_0.1.9-1_arm64.deb` | qrbin for 64-bit ARM. |
| `pool/main/s/smashbin/smashbin_0.1.5-1_amd64.deb` | smashbin for 64-bit Intel and AMD. |
| `pool/main/s/smashbin/smashbin_0.1.5-1_arm64.deb` | smashbin for 64-bit ARM. |
| `pool/main/r/rmbin/rmbin_0.0.1-1_amd64.deb` | rmbin for 64-bit Intel and AMD. |
| `pool/main/r/rmbin/rmbin_0.0.1-1_arm64.deb` | rmbin for 64-bit ARM. |
| `pool/main/r/rmbin/rmbin_0.0.1-1_armhf.deb` | rmbin for 32-bit ARM. |
| `pool/main/r/rmbin/rmbin_0.0.1-1_i386.deb` | rmbin for 32-bit Intel and AMD. |

`apt-get update` reads `InRelease` and then the `Packages` file for your architecture. `apt-get install` uses the path inside `Packages` to download one `.deb` from `pool/`. The `.deb` unpacks to `/usr/bin/qrbin`, `/usr/bin/smashbin`, or `/usr/bin/rmbin`. The first letter of the package name is the folder under `pool/main/`: `q` for qrbin, `s` for smashbin, `r` for rmbin.

Publishing a new version is a separate job, done on the Mac that holds the signing key. That procedure is [release.md](release.md).

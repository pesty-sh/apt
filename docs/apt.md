# Apt, from the first command

This is the install guide for someone who has not used `apt-get` before. It installs [qrbin](https://github.com/pesty-sh/qrbin), a program that turns text into a QR code image and does not contact the network while it runs.

You do this on an Ubuntu or Debian computer. On a Mac, the install is Homebrew: `brew install pesty-sh/tap/qrbin`.

The short list of commands is on the [front page](../README.md). This page explains what each one does, how to check the computer you are on, and what the usual messages mean.

## The words

You will see these words in the commands and in apt's output.

| Word | Meaning |
|---|---|
| Package | A named program apt can install. The name here is `qrbin`. |
| `.deb` | The file apt downloads. It holds the program and a short description. |
| Repository | A website with a package list and the `.deb` files. This one is `https://pesty-sh.github.io/apt`. |
| `apt-get` | The command that reads the list, downloads a package, and unpacks it. `apt` is the same tool with a slightly shorter prompt. Both work. The commands below use `apt-get`. |
| `sudo` | Runs the command as the administrator. Apt needs it because the program is installed for every user on the computer. |
| Source list | A text file that tells apt which repositories exist. Yours will be `/etc/apt/sources.list.d/pesty.list`. |
| Key | A small file apt uses to check the signature on the package list. You save it once. |
| Suite | The channel name inside the repository. Ours is `stable`. |
| Component | The section inside the suite. Ours is `main`. |
| Architecture | The kind of processor. `amd64` is Intel and AMD. `arm64` is 64-bit ARM. |

`0.1.9-1` is the package version. `0.1.9` is the qrbin version. `-1` means the first time that version was packed into a `.deb`.

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

`amd64` or `arm64` is what this repository publishes. Apt matches that word to the package by itself when you install.

You also need a network connection for the install. qrbin does not use the network after that. The download is a few megabytes.

## 1. Save the key

Apt will not use a repository until it can check a signature. The public key is safe to download. The private half stays with the person who publishes qrbin.

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
| `main` | The section. qrbin is published in `main`. |

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

## Upgrade

When a newer package is published, the source line stays as it is. Refresh the list, then install again:

```bash
sudo apt-get update
sudo apt-get install qrbin
```

If the machine already has the newest published version, apt says qrbin is already the newest version and leaves the file in place.

`sudo apt-get upgrade` upgrades every installed package that has a newer version in any of your repositories, including qrbin. Use the two commands above when you want to upgrade qrbin on its own.

## Remove

Remove the program and keep the configuration apt stored for it:

```bash
sudo apt-get remove qrbin
```

Remove the program and that stored configuration:

```bash
sudo apt-get purge qrbin
```

The repository line remains, so a later `sudo apt-get install qrbin` works without repeating steps 1 and 2. To stop apt from looking at this repository, delete the list file and refresh:

```bash
sudo rm /etc/apt/sources.list.d/pesty.list
sudo apt-get update
```

The key file can stay in `/usr/share/keyrings`. It is unused once the list file is gone.

## When a command fails

Read the last lines apt printed. These are the ones people hit on a first install.

**`Could not get lock` / `Unable to acquire the dpkg frontend lock`.** Another apt command is still running, often a software updater in the background. Wait for it to finish. Then run the command again.

**`Unable to locate package qrbin`.** Apt does not have this repository in its list yet. Check the file:

```bash
cat /etc/apt/sources.list.d/pesty.list
```

The line should match step 2 exactly. Then run `sudo apt-get update` again, and `apt-cache policy qrbin`. The policy output has to mention `pesty-sh.github.io` before `install` can find the package.

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
| `dists/stable/main/binary-amd64/Packages` | The list of Intel and AMD packages: name, version, file size, checksum, and path. |
| `dists/stable/main/binary-arm64/Packages` | The same list for 64-bit ARM. |
| `pool/main/q/qrbin/qrbin_0.1.9-1_amd64.deb` | The Intel and AMD package. |
| `pool/main/q/qrbin/qrbin_0.1.9-1_arm64.deb` | The 64-bit ARM package. |

`apt-get update` reads `InRelease` and then the `Packages` file for your architecture. `apt-get install` uses the path inside `Packages` to download one `.deb` from `pool/`. The `.deb` unpacks to `/usr/bin/qrbin`.

Publishing a new version is a separate job, done on the Mac that holds the signing key. That procedure is [release.md](release.md).

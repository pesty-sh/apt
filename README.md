# Install pesty-sh packages with apt

This folder is the package repository apt reads. On the publishing Mac it is `/Users/developers/Projects/pesty-sh/apt`. On GitHub it is [pesty-sh/apt](https://github.com/pesty-sh/apt). Apt downloads it from `https://pesty-sh.github.io/apt`. Homepage: [pesty.sh](https://pesty.sh).

On Ubuntu and Debian you install these programs with `apt-get`, the program those systems already use to install software.

| Package | What it does | Version | Architectures |
|---|---|---|---|
| [qrbin](https://github.com/pesty-sh/qrbin) | Turns text into a QR code image. It does not use the network. | `0.1.9-1` | `amd64`, `arm64` |
| [smashbin](https://github.com/pesty-sh/smashbin) | Strips metadata and shrinks a PNG, JPG, or GIF. It does not use the network. | `0.1.5-1` | `amd64`, `arm64` |
| [rmbin](https://github.com/pesty-sh/rmbin) | Overwrites a file you name with a repeating text pattern, syncs that write to disk, then deletes the file. It does not use the network. | `0.0.1-1` | `amd64`, `arm64`, `armhf`, `i386` |

`0.1.9-1` means program version `0.1.9` and Debian package revision `1` (the first time that version was packed into a `.deb`). smashbin and rmbin use the same pattern.

rmbin permanently deletes the paths you give it. There is no warranty, and the authors accept no liability for lost files. Installing or removing the package only adds or removes `/usr/bin/rmbin`. It does not delete your files. Overwriting is best effort on SSDs, copy-on-write filesystems, snapshots, and backups. The check further down is `rmbin --version` and a dry run. Neither one deletes anything. Read the [disclaimer](https://github.com/pesty-sh/rmbin/blob/v0.0.1/DISCLAIMER.md) before you point rmbin at a real file.

## What apt does

You tell `apt-get` a package name. It downloads a `.deb` file (a small archive that contains the program), checks that the file was signed by the key you saved, and unpacks the program into `/usr/bin`.

Ubuntu's archive and Debian's archive do not contain these packages. The four commands below teach apt about this repository. You run them once. After that, installing and upgrading is the same kind of command you use for any other package.

These systems can install the packages:

| System | Works |
|---|---|
| Ubuntu 18.04, 20.04, 22.04, 24.04 | yes |
| Debian 10, 11, 12, 13 | yes |

qrbin and smashbin need `libc6` version 2.27 or newer, which those releases already have. rmbin's `.deb` does not depend on `libc6`. Its own release notes name Ubuntu 14.04 and Debian 8 as the floor for that static build. The table above is the set of systems this install guide covers.

Apt picks the build for the machine. You do not type the architecture yourself.

| Architecture | Machine | Packages |
|---|---|---|
| `amd64` | 64-bit Intel and AMD | qrbin, smashbin, rmbin |
| `arm64` | 64-bit ARM, including a Raspberry Pi 4 or 5 running a 64-bit system | qrbin, smashbin, rmbin |
| `armhf` | 32-bit ARM | rmbin |
| `i386` | 32-bit Intel and AMD | rmbin |

On a Mac, the install is Homebrew: `brew install pesty-sh/tap/qrbin`, `brew install pesty-sh/tap/smashbin`, or `brew install pesty-sh/tap/rmbin`.

The long version of this page, with a check of your system and the messages you may see, is [docs/apt.md](docs/apt.md).

## Install

Open a terminal on the Ubuntu or Debian computer. The keystroke on Ubuntu is Ctrl+Alt+T. Run the commands in this order.

Save the signing key. Apt uses it to check that the package list came from pesty-sh. The fingerprint of this key is `2564 D17C 2F8B EC6A 9E59 6BB0 2B0D 9ACE 648D D6FF`.

```bash
sudo mkdir -p /usr/share/keyrings
curl -fsSL https://pesty-sh.github.io/apt/pesty-archive-keyring.gpg \
  | sudo tee /usr/share/keyrings/pesty-archive-keyring.gpg >/dev/null
```

Tell apt the address of this repository. That writes `/etc/apt/sources.list.d/pesty.list`.

```bash
echo "deb [signed-by=/usr/share/keyrings/pesty-archive-keyring.gpg] https://pesty-sh.github.io/apt stable main" \
  | sudo tee /etc/apt/sources.list.d/pesty.list
```

`stable` is the channel name. `main` is the section. qrbin, smashbin, and rmbin are all in that one channel.

Download the package list:

```bash
sudo apt-get update
```

Install the program you want:

```bash
sudo apt-get install qrbin
```

```bash
sudo apt-get install smashbin
```

```bash
sudo apt-get install rmbin
```

`sudo` asks for your password because these commands write into system folders. The program is then `/usr/bin/qrbin`, `/usr/bin/smashbin`, or `/usr/bin/rmbin`. `/usr/bin` is already on your `PATH`.

## See that it worked

qrbin prints its version, then writes a QR image of the word hello:

```bash
qrbin --version
qrbin hello > hello.png
```

Open `hello.png` in the image viewer.

smashbin prints its version:

```bash
smashbin --version
```

rmbin prints its version. The dry run shows the plan for a throwaway file and does not delete it. Without `--yes`, rmbin would ask you to type `yes` before changing a file. `--dry-run` changes nothing either way.

```bash
rmbin --version
printf 'hello\n' > /tmp/rmbin-example.txt
rmbin --dry-run /tmp/rmbin-example.txt
```

`rmbin --version` prints `rmbin 0.0.1`.

## A newer version later

```bash
sudo apt-get update
sudo apt-get install qrbin
```

Use `smashbin` or `rmbin` in place of `qrbin` to upgrade that package. `update` downloads the list again. `install` replaces the program in `/usr/bin` when the published version is newer than the one on the machine.

## More

* [docs/apt.md](docs/apt.md) is the full first-time tutorial: what the words mean, how to see your Ubuntu version, and what to do when a command prints an error.
* [docs/release.md](docs/release.md) is for publishing the next `.deb` from the Mac that keeps the signing key.

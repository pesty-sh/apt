# Install qrbin with apt

qrbin turns text into a QR code image. On Ubuntu and Debian you install it with `apt-get`, the program those systems already use to install software.

This folder is the package repository apt reads. On the publishing Mac it is `/Users/developers/Projects/pesty-sh/apt`. On GitHub it is [pesty-sh/apt](https://github.com/pesty-sh/apt). Apt downloads it from `https://pesty-sh.github.io/apt`.

The program's source is [pesty-sh/qrbin](https://github.com/pesty-sh/qrbin). Homepage: [pesty.sh](https://pesty.sh).

## What apt does

You tell `apt-get` a package name. It downloads a `.deb` file (a small archive that contains the program), checks that the file was signed by the key you saved, and unpacks the program into `/usr/bin`.

Ubuntu's archive and Debian's archive do not contain qrbin. The four commands below teach apt about this repository. You run them once. After that, installing and upgrading qrbin is the same kind of command you use for any other package.

The package name is `qrbin`. The version published here is `0.1.9-1`. The `0.1.9` is the program version. The `-1` means this is the first package build of that version.

These systems can install it:

| System | Works |
|---|---|
| Ubuntu 18.04, 20.04, 22.04, 24.04 | yes |
| Debian 10, 11, 12, 13 | yes |

Apt picks the build for the machine. Intel and AMD use `amd64`. 64-bit ARM (including a Raspberry Pi 4 or 5 running a 64-bit system) uses `arm64`. You do not type the architecture yourself.

On a Mac, the install is Homebrew: `brew install pesty-sh/tap/qrbin`.

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

`stable` is the channel name. `main` is the section. Every qrbin package is in that one channel, on every Ubuntu and Debian release in the table above.

Download the package list:

```bash
sudo apt-get update
```

Install the program:

```bash
sudo apt-get install qrbin
```

`sudo` asks for your password because these commands write into system folders. The program is then `/usr/bin/qrbin`, which is already on your `PATH`.

## See that it worked

```bash
qrbin --version
```

Write a QR image of the word hello:

```bash
qrbin hello > hello.png
```

Open `hello.png` in the image viewer.

## A newer version later

```bash
sudo apt-get update
sudo apt-get install qrbin
```

`update` downloads the list again. `install` replaces `/usr/bin/qrbin` when the published version is newer than the one on the machine.

## More

* [docs/apt.md](docs/apt.md) is the full first-time tutorial: what the words mean, how to see your Ubuntu version, and what to do when a command prints an error.
* [docs/release.md](docs/release.md) is for publishing the next `.deb` from the Mac that keeps the signing key.

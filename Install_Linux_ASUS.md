# Install Linux on ASUS Laptops

Hi everyone and welcome to the resistance!  
This is a comprehensive guide on how to install Linux on your ASUS laptop, based on personal experience and created with the help of the amazing community at **OpenGamingCollective (OGC)** and **asus-linux**.

We at the [OpenGamingCollective](https://opengamingcollective.org/) (OGC) are a group of developers, gamers, and enthusiasts who seek to get the absolute most out of our hardware — from daily productivity to high-performance gaming — free from the constraints of operating systems that compromise your privacy and restrict your freedom of choice.

In particular, the [asus-linux](https://asus-linux.org/) project maintains [asusctl](https://github.com/OpenGamingCollective/asusctl) and [ROG Control Center](https://github.com/OpenGamingCollective/asusctl) to give you total hardware control over ASUS ROG, TUF, Zephyrus, Ally, and ZenBook laptops under Linux (including power profiles, fan curves, custom TDP limits, AniMe Matrix, and Aura RGB lighting).

---

## 🎒 What You Need Before Starting

1. **An ASUS Laptop** (ROG Strix, Zephyrus, TUF, ROG Ally, ZenBook, Vivobook, etc.)
2. **Windows** (Yes, really — we need Windows temporarily to extract factory hardware parameters for unsupported models!)
3. **A Linux Distro ISO** (Officially supported: **Arch Linux** and Arch-based distributions like EndeavourOS, Manjaro, CachyOS)
4. **A USB Flash Drive** (At least 8 GB, USB 3.0 recommended)
5. **Some free time and patience**

---

## 💻 1. Checking Hardware Support & Preparing Windows

### Identifying Your Exact Laptop Model
You need your exact laptop model string (e.g. `ROG Strix SCAR 17 G713QM`, `Zephyrus G14 GA402RJ`, `TUF Gaming A15 FA507XI`, `ROG Ally RC71L`). You can find this model number on:
* The original retail box or sticker on the bottom of the chassis
* In your laptop's BIOS/UEFI main screen
* By running `wmic csproduct get name` in Windows Command Prompt

### Verifying Upstream Kernel & `asus-linux` Support
Check whether your laptop model and features are supported:
* Upstream Linux kernel driver support: [`asus-armoury.h`](https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git/tree/drivers/platform/x86/asus-armoury.h)
* Keyboard Aura RGB support database: [`aura_support.ron`](https://github.com/OpenGamingCollective/asusctl/blob/main/rog-aura/data/aura_support.ron)

If your laptop is listed, hardware control works out of the box! If it's a brand-new or unlisted model, you can still install Linux seamlessly, but you'll want to follow the section below to help us extract TDP parameters.

### Extracting `ThrottleGear_*.xml` (Goldmine for New Hardware!)
If your laptop is a new generation or not yet explicitly listed, Armoury Crate in Windows contains the factory TDP power tables, boost limits, and fan curve limits:

1. Boot into Windows and update **Armoury Crate** to the latest version.
2. Navigate to:
   * `C:\Program Files\ASUS\Armoury Crate\`
   * or `C:\ProgramData\ASUS\` (enable "Show hidden files" in File Explorer)
3. Search for a file matching: `ThrottleGear_*your_model*.xml` (e.g. `ThrottleGear_G713QM.xml`).
4. Copy this file to a safe place (e.g. cloud storage or a secondary USB drive). This file contains encrypted TDP parameters for the CPU/GPU that allow us to add native support for your laptop model!

---

## 💿 2. Selecting Your Linux Distro & Preparing the USB

### Distro Compatibility Rules
To ensure 100% compatibility with `asusctl` and `rog-control-center`:
* **Official Distro Support**: Arch Linux and Arch-based OSes (EndeavourOS, CachyOS, Manjaro).
* **Display Server**: **Wayland** is required for modern multi-GPU dynamic switching, panel refresh rate switching, and display scaling (X11 is deprecated and unsupported).
* **Init System**: **systemd** is strictly required (OpenRC, runit, or s6 are unsupported).
* **Kernel Version**: We strongly recommend Linux Kernel **6.19+** (preferably the latest stable kernel, required for native `asus-armoury` and firmware attribute support).

### Flashing the USB Drive
1. Insert your USB drive (at least 8 GB).
2. Download [Rufus](https://rufus.ie/) (Windows) or use `dd` / [Impression](https://flathub.org/apps/io.gitlab.mrvik.Impression) (Linux).
3. In Rufus:
   * Select your downloaded Arch/Arch-based ISO.
   * Select **GPT** partition scheme and **UEFI (non CSM)** target system.
   * Click **Start** and wait ~5–10 minutes for flashing to finish.

---

## ⚙️ 3. BIOS / UEFI Settings (Crucial Step!)

1. Shut down your laptop completely.
2. Turn it on and immediately tap **F2** (or **Del**) repeatedly to enter BIOS setup.
3. Switch to **Advanced Mode** (usually **F7**).
4. Configure the following mandatory BIOS settings:
   * **Secure Boot**: Set to **Disabled** (found under the *Security* or *Boot* tab).
   * **Fast Boot**: Set to **Disabled**.
   * **VMD Controller / Intel RST** (Intel models only): If enabled, switch storage mode to **AHCI / NVMe** so Linux can detect your SSDs.
   * **Graphics Mode**: Set GPU mode to **Hybrid** or **Standard** for initial installation.
5. Set your USB drive as **Boot Option #1** (or tap **F8** during boot to bring up the UEFI Boot Menu).
6. Save & Exit (**F10**).

---

## 🚀 4. Installing the OS & Setting up `asusctl`

Follow your chosen distribution's installer (e.g. `archinstall` for Arch Linux, or the Calamares installer for EndeavourOS/CachyOS). Make sure to choose a Wayland desktop environment (**KDE Plasma 6** or **GNOME 46+** are recommended).

Once booted into your new Linux installation:

### Step 1: Add the Official OGC Pacman Repository
We maintain pre-compiled, optimized packages for Arch Linux in the official OGC repository (avoid outdated AUR packages).

Open your terminal and edit `/etc/pacman.conf`:
```bash
sudo nano /etc/pacman.conf
```

Add the `[ogc]` repository block **above** all other repository definitions (above `[core]`):
```ini
[ogc]
SigLevel = Optional TrustAll
Server = https://pacman.opengamingcollective.org/repo/$arch
```

Save and exit (`Ctrl+O`, `Enter`, `Ctrl+X`).

### Step 2: System Update & Package Installation
Update your pacman package database and install `rog-control-center` (this will automatically pull `asusctl`, `asusd`, and all required dependencies):

```bash
sudo pacman -Syu
sudo pacman -S rog-control-center
```

### Step 3: Enable & Start the Background Daemon
Enable and start the `asusd` system service and user session service:

```bash
sudo systemctl enable --now asusd
systemctl --user enable --now asusd-user
```

### Step 4: Verify Hardware Control
Launch `rog-control-center` from your application menu or terminal:

```bash
rog-control-center
```

* **System Control Tab**: Adjust CPU/GPU TDP sliders, thermal profiles (Quiet, Balanced, Performance), fan curves, and battery charge limits (e.g. 60%, 80%, 100%).
* **Keyboard Aura Tab**: Customize RGB lighting effects, per-zone colors, and brightness.
* **CLI Control**: You can also use the `asusctl` CLI tool in terminal:
  ```bash
  asusctl info                 # Print hardware & daemon status
  asusctl profile -n            # Cycle power profiles (Quiet -> Balanced -> Performance)
  asusctl aura static -c ff0000 # Set static red keyboard backlight
  ```

---

## 🎉 Conclusion & How to Submit `ThrottleGear` Files

Congratulations! You now have a high-performance Linux system running on your ASUS laptop with full hardware control.

### Have an Unsupported Model or `ThrottleGear_*.xml` File?
If your laptop model was unlisted or missing custom TDP profiles:
1. Join our community on the [OpenGamingCollective Discord](https://discord.gg/ugAKk6peK).
2. Reach out directly to **@scardracs** or post in the hardware support channel.
3. Alternatively, open a new issue on the [asusctl GitHub Repository](https://github.com/OpenGamingCollective/asusctl/issues/new) and attach your extracted `ThrottleGear_*.xml` file.

Your contribution helps us add native Linux support for your laptop model for the entire community! 🚀

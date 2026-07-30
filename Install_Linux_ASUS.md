# Install Linux on ASUS Laptops
Hi everyone and welcome to the resistance.  
This is a little guide of mine on how to install linux on your Asus laptop, based on my personal experience and with the help of the amazing family named the OpenGamingCollective!  
We at the [OpenGamingCollective](https://opengamingcollective.org/), shortend in OGC, are a group of people who seek to take the most out of our device, from work to gaming (especially gaming)to daily life activities, free of the burden of an OS who want to control your life, sell your privacy and take away your freedom of choice.

In particular, We at [asus-linux](https://asus-linux.org/) use [ROG Control Center](https://github.com/OpenGamingCollective/asusctl) to control our laptops, from power profiles to rgb lights (on supported models).

First of all, You need 5 things:

- An Asus Laptop (duh!)
- Windows (WAT!?) - Yeah, We need WeirDOS and You'll find out why below
- The ISO of the Linux Distro You want to install (REMEMBER - We in asus-linux only officially support Arch and Arch based OSes)
- A USB Key where to flash your OS
- Some free time (and a lot of patience)

Now, without further ado, let's begin.

## Asus Laptop
As I said before, We need an Asus Laptop. To be precise We need its exact model number (for eg., ROG Strix SCAR 17 G713QM, VivoBook S15 S533J, etc. in case you're wondering). You can find it on the box of your laptop, on a sticker on the bottom of the laptop, or in the BIOS. You need this information to check in the Linux repo if your laptop is supported by [linux](https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git/tree/drivers/platform/x86/asus-armoury.h) and by [asus-linux](https://github.com/OpenGamingCollective/asusctl/blob/main/rog-aura/data/aura_support.ron). If your laptop is listed, You are good to go. If not, You can still install it but You will miss advance power control and keyboard lights.

In the case your device is not supported, don't worry! I gotchya covered.

## Windows
This passage is specific for those who don't have a device model listed on the previous section. If your model is listed You can skip this section and go directly to the next one (but I still suggest You to follow it because that file is like gold to us). All We need is Armoury Crate at its latest version! Remember, it must be the latest version!

Done that? Good. Now, You should check inside C:\Program Files\ASUS\Armoury Crate\ or C:\ProgramData\ for a file named ThrottleGear_*your model*.xml. It's an encrypted file that contains the specs of your laptop for the TDP of the GPU and the CPU. We will need this later so be sure to save it somewhere safe.

## The ISO of the Linux Distro You want to install
Now, We can finally get to the fun part. You need to get an ISO of the Linux distro You want to install. Remeber, We only officially support Arch and Arch based OSes. If You want to use another distro, I wish You good luck (even more if You want to intall something like Ubuntu or any other .deb based distro as We don't support them). Also, remember We don't support OSes with x11 (only Wayland) and init systems other than systemd (no OpenRC, runit, s6, etc). If You don't know what these are, just stick to Arch or an Arch based OS.

## A USB Key
Now that We are done with the pleasentries, let's get to the practical part. You need at least a 8GB key to be sure it will not fail You because too little space. For our guide I suggest [Rufus](https://rufus.ie/) to flash the ISO. You simply select your ISO in the ISO field, select your USB key in the Device field, select GPT partition scheme and press start. In 10 minutes You should have your bootable usb key ready.

## Some free time
Now the real hassle. First of all You need to boot into your BIOS. Turn off your laptop, then turn it on again and start pushing like your life depends on it F2 or Canc or Esc: it depends on your model. Done that, You should be in a blueish (depending on the model) screen. Now, look around for "Secure Boot" and disable it (it's in boot or security tab usually). You should also set your USB Key as the primary boot device. If You  have any doubt about these passages feel free to crash in our [OGC Discord](https://discord.gg/ugAKk6peK) and ask away. If You are good to go, now You can reboot and proceed with the installation.

## Installation
I won't guide You on how to install your OS because it depends on your choice. If You have decided for vanilla Arch, I wish You good luck and I redirect You to the [ArchWiki](https://wiki.archlinux.org/title/Installation_guide) for further instructions. If You have decided for an Arch based distro with graphical install, it will be much easier to follow. In any case, when you'll be in your new Linux OS, be sure to follow the following steps:

1. Find out the correct repo (for Arch and Arch based OSes I don't suggest the one in AUR because it's not maintained by Us). We officially maintain [Our repo](https://pacman.opengamingcollective.org/). You can add it to your system by running the following commands:
    - We need to modify the pacman.conf to add the needed ogc repo  
    ```bash
    sudo nano /etc/pacman.conf
    ```
    - Bedore any other repos add these lines:
    ```bash
    [ogc]
    SigLevel = Optional TrustAll
    Server = https://pacman.opengamingcollective.org/repo/$arch
    ```
2. Now update your system packages. It will ask You to import a new key. Ofc say Yes!
    ```bash
    sudo pacman -Syu
    ```
    - And now You can install rog-control-center! It will pick up all the needed packages for you
    ```bash
    sudo pacman -S rog-control-center
    ```
3. You can start rog-control-center and be good to go!
    - Under App Settings, You can find that there's a voice to start the app at boot: personally I suggest it so You don't have to start it manually every time at every boot.
    - On System Control, You can easily find if your device is officially supported, because You'll see a bunch of sliders where to decide the TDP of the CPU and GPU.
    - Under Keyboard Aura, You can decide which Aura effect use. If your device is not officially supported, only the static mode will works.

## Conclusions
That's it! You now have a working Linux OS on your ASUS laptop. I hope this guide helped You. If You still have any doubts, suggestions or anything else, feel free to ask in our [OGC Discord](https://discord.gg/ugAKk6peK).

## And the ThrottleGear?
You thought We'd forget about it? No way!  
If your device is not supported and you pick up the ThrottleGear xml file, check out for me, @scardracs, on our [Discord](https://discord.gg/ugAKk6peK). This file will help on adding your device to the supported ones or, even better, You can open a [new issue on our Github](https://github.com/OpenGamingCollective/asusctl/issues/new) and submit the ThrottleGear file You found in the folder I said earlier.
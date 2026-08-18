# 🐛 Active Upstream Issues & Roadmap Mapping

> *Last automated synchronization: 2026-08-18 16:19 UTC*

This document provides an automated classification of all **active open issues** from [`OpenGamingCollective/asusctl`](https://github.com/OpenGamingCollective/asusctl/issues).

Issues are categorized by subsystem and functional domain, detailing their root causes and mapping them directly to our architectural refactoring roadmap, pull requests, and engineering invariants.

---

## 📑 Issue Category Index

1. [🔋 Power Management, GPU Switching & Zero-Wakeup Telemetry](#-power-management-gpu-switching-zero-wakeup-telemetry)
2. [⚡ Concurrency, D-Bus Deadlocks & Async Task Lifecycles](#-concurrency-d-bus-deadlocks-async-task-lifecycles)
3. [🛡️ Crashes, Panics & Protocol Robustness (Zero-Unwrap Invariant)](#-crashes-panics-protocol-robustness-zero-unwrap-invariant)
4. [⌨️ Hardware Quirks, Keyboard Backlight & DMI Taxonomy Engine](#-hardware-quirks-keyboard-backlight-dmi-taxonomy-engine)
5. [🖥️ GUI (`rog-control-center`) & CLI (`asusctl`) Ergonomics](#-gui-rog-control-center-cli-asusctl-ergonomics)
6. [📦 Packaging, Distribution & Ecosystem Integration](#-packaging-distribution-ecosystem-integration)

---

## 1. 🔋 Power Management, GPU Switching & Zero-Wakeup Telemetry

| Issue # | Title | Subsystems | Status / Fix Verification | Architectural Resolution & Roadmap Link |
| :--- | :--- | :--- | :---: | :--- |
| **[#318](https://github.com/OpenGamingCollective/asusctl/issues/318)** | [Bug]: GPU mode switch via rog-control-center not appli... | `bug`, `rog-control-center`, `asusd` | ⚠️ **ACTIVE BUG** | **Phase 2.1 / 2.2: Normalize kernel sysfs return codes (EEXIST / no-op writes) during shutdown sync** |
| **[#302](https://github.com/OpenGamingCollective/asusctl/issues/302)** | [Bug]: dGPU still resumed every 2 s on 6.4.0 — #294's g... | `bug`, `rog-control-center`, `rog-platform` | ⚠️ **ACTIVE BUG** | **Phase 1.1 / Section 3.3: Extend zero-wakeup check to inspect entire PCI sub-tree (including GPU Audio 01:00.1)** |
| **[#288](https://github.com/OpenGamingCollective/asusctl/issues/288)** | [Bug]: AniMe Matrix power-state handlers are not starte... | `bug`, `asusd`, `rog-anime` | 🟢 **IN PR (#317)** | **PR #317 / PR #290: Dedicated AniMe task lifecycle initialization with power state evaluation** |
| **[#264](https://github.com/OpenGamingCollective/asusctl/issues/264)** | [Documentation Bug]: Recommend 'systemctl mask' for pow... | `bug`, `documentation`, `rog-profiles` | ✅ **RESOLVED UPSTREAM** | **Fixed via PR #303 (commit `5307fd13`): Added power-profiles-daemon masking recommendation** |
| **[#250](https://github.com/OpenGamingCollective/asusctl/issues/250)** | Support request: ASUS V16 V3607VM — pwm1/pwm2 fan contr... | `bug`, `enhancement`, `rog-profiles` | ⚠️ **ACTIVE BUG** | **Phase 2.2: Extend rog-platform EC mailbox probe to recognize Vivobook V3607 series EC tables** |
| **[#204](https://github.com/OpenGamingCollective/asusctl/issues/204)** | FX507ZM: Enabling custom fan curves causes NVIDIA GPU t... | `general` | ⚠️ **ACTIVE BUG** | **Phase 2.2: EC firmware quirk on 2022 TUF models where manual fan tables reset dynamic boost budget** |
| **[#196](https://github.com/OpenGamingCollective/asusctl/issues/196)** | Fan curves for Quiet profile silently reverted to enabl... | `general` | ⚠️ **ACTIVE BUG** | **Phase 2.5: Preserve user-configured custom curve enable states in daemon memory across ACPI switches** |
| **[#162](https://github.com/OpenGamingCollective/asusctl/issues/162)** | GA401QE: Custom fan curves are not reapplied after AC p... | `general` | 🟢 **IN PR (#316)** | **PR #316 / Phase 2.5: Re-apply custom fan curve tables immediately upon logind power transition events** |
| **[#153](https://github.com/OpenGamingCollective/asusctl/issues/153)** | Battery charge limit not enforced on ASUS Vivobook 16 V... | `general` | ⚠️ **ACTIVE BUG** | **Phase 2.2: Fallback to /sys/class/power_supply/BAT0/charge_control_end_threshold with direct WMI EC** |
| **[#152](https://github.com/OpenGamingCollective/asusctl/issues/152)** | Boot freeze at Plasma desktop on AC→battery transition,... | `general` | 🟢 **IN PR (#310)** | **PR #310 / Phase 1.4: Eliminate asusd-user.service to prevent dual-daemon race conditions and freeze loops** |
| **[#145](https://github.com/OpenGamingCollective/asusctl/issues/145)** | CPU power limit settings do not take effect (overriden ... | `general` | ⚠️ **ACTIVE BUG** | **Phase 2.2: Direct Intel RAPL sysfs top-level zone writes bypassing MMIO locking** |
| **[#136](https://github.com/OpenGamingCollective/asusctl/issues/136)** | Fan curves desync from platform profile after boot (bal... | `general` | ⚠️ **ACTIVE BUG** | **Phase 2.5 / PR #316: Fan curve synchronization with platform profile upon boot initialization** |
| **[#132](https://github.com/OpenGamingCollective/asusctl/issues/132)** | asusd: one firmware-rejected attribute (nv_dynamic_boos... | `general` | ✅ **RESOLVED UPSTREAM** | **Fixed in commit `ab1b72b6`: Skip failing Armoury attributes with `continue` instead of aborting** |
| **[#129](https://github.com/OpenGamingCollective/asusctl/issues/129)** | GPU control over iGPU and dGPU lost, with system tray i... | `general` | ⚠️ **ACTIVE BUG** | **Phase 1.1 / 2.1: Prevent GPU tray desync by subscribing directly to udev drm event stream** |
| **[#117](https://github.com/OpenGamingCollective/asusctl/issues/117)** | rog-control-center Charge Limit No Longer Working... | `general` | ✅ **RESOLVED UPSTREAM** | **Fixed in commit `ab1b72b6`: Charge limit sysfs path and D-Bus proxy binding updated** |
| **[#112](https://github.com/OpenGamingCollective/asusctl/issues/112)** | Fans are not following their profiles after connecting/... | `general` | 🟢 **IN PR (#316)** | **PR #316 / Phase 2.5: Re-evaluate fan curve profile automatically upon AC/Battery transition** |
| **[#100](https://github.com/OpenGamingCollective/asusctl/issues/100)** | CPU is heavily power limited (Zephyrus M16 2023)... | `general` | ⚠️ **ACTIVE BUG** | **Phase 2.2: Intel RAPL / MSR TDP floor unlock on Zephyrus M16 2023** |
| **[#82](https://github.com/OpenGamingCollective/asusctl/issues/82)** | Show OSD notification on power profile change... | `general` | 💡 **FEATURE REQUEST** | **Phase 3.4: Trigger desktop OSD notifications via org.freedesktop.Notifications on profile cycle** |
| **[#68](https://github.com/OpenGamingCollective/asusctl/issues/68)** | Add Static and BatteryLevel modes for slash lighting... | `general` | 💡 **FEATURE REQUEST** | **Phase 2.4: Add Static and BatteryLevel modes for slash lighting controllers** |

---

## 2. ⚡ Concurrency, D-Bus Deadlocks & Async Task Lifecycles

| Issue # | Title | Subsystems | Status / Fix Verification | Architectural Resolution & Roadmap Link |
| :--- | :--- | :--- | :---: | :--- |
| **[#232](https://github.com/OpenGamingCollective/asusctl/issues/232)** | asusd-user crashes on startup: DBus path mismatch for A... | `general` | 🟢 **IN PR (#310)** | **PR #310 / Phase 1.4: Purge asusd-user crate entirely. All clients communicate with asusd system D-Bus** |
| **[#229](https://github.com/OpenGamingCollective/asusctl/issues/229)** | rog-control-center leaks a D-Bus connection per poll an... | `general` | ✅ **RESOLVED UPSTREAM** | **Fixed in PR #315 (commit `31635a6f`): Persistent zbus::Connection proxy pool in rog-control-center** |

---

## 3. 🛡️ Crashes, Panics & Protocol Robustness (Zero-Unwrap Invariant)

| Issue # | Title | Subsystems | Status / Fix Verification | Architectural Resolution & Roadmap Link |
| :--- | :--- | :--- | :---: | :--- |
| **[#304](https://github.com/OpenGamingCollective/asusctl/issues/304)** | [Bug]: rog-control-center panics when config file is re... | `bug`, `rog-control-center` | 🟢 **IN PR (#305)** | **PR #305 / Invariant #5: Remove `.unwrap()` in config-traits; fallback gracefully when file is read-only** |
| **[#159](https://github.com/OpenGamingCollective/asusctl/issues/159)** | rog-control-center panics on GZ302: duplicate entry in ... | `general` | ✅ **RESOLVED UPSTREAM** | **Fixed in commit `48daeaab`: Deduplicated GZ302 entry in aura_support.ron** |

---

## 4. ⌨️ Hardware Quirks, Keyboard Backlight & DMI Taxonomy Engine

| Issue # | Title | Subsystems | Status / Fix Verification | Architectural Resolution & Roadmap Link |
| :--- | :--- | :--- | :---: | :--- |
| **[#284](https://github.com/OpenGamingCollective/asusctl/issues/284)** | [Device Support]: TUF Gaming A18 FA808UM — backlight wo... | `bug`, `enhancement`, `asusd` | 🟢 **IN PR (#147)** | **Phase 2.4 (dmi-id) / PR #147: LampArray HID transport backend selection in rog-aura** |
| **[#263](https://github.com/OpenGamingCollective/asusctl/issues/263)** | [Device Support]: No keyboard backlight on ASUS TUF Gam... | `bug`, `enhancement`, `asusd` | ⚠️ **ACTIVE BUG** | **Phase 2.4 (dmi-id): Add FA608PP model family quirk mapping to route backlight via WMI EC registers** |
| **[#225](https://github.com/OpenGamingCollective/asusctl/issues/225)** | Add Aura support for ASUS TUF Gaming A16 FA608PP... | `general` | ⚠️ **ACTIVE BUG** | **Phase 2.4 (dmi-id): Add Aura support for ASUS TUF Gaming A16 FA608PP** |
| **[#210](https://github.com/OpenGamingCollective/asusctl/issues/210)** | (rog-control-center): App window closes immediately whe... | `general` | ⚠️ **ACTIVE BUG** | **Phase 3.4: Decouple window close event from daemon background runtime in rog-control-center** |
| **[#169](https://github.com/OpenGamingCollective/asusctl/issues/169)** | Add Aura support for G614PM (ROG Strix G16)... | `general` | ✅ **RESOLVED UPSTREAM** | **Fixed in PR #307 (commit `a1322ff9`): Added Aura support for ROG Strix G16 G614PM** |
| **[#165](https://github.com/OpenGamingCollective/asusctl/issues/165)** | [Flow Z13 2025] External touchpad does not work when ke... | `general` | ⚠️ **ACTIVE BUG** | **Phase 1.1 / 2.1: Maintain SCSI keep-alive polling on tablet base controller even when keyboard detaches** |
| **[#151](https://github.com/OpenGamingCollective/asusctl/issues/151)** | Keyboard backlight non-functional on ASUS TUF Gaming A1... | `general` | 🟢 **IN PR (FA401WU)** | **Branch `FA401WU` (commit `de53c4bd`): Keyboard backlight support for ASUS TUF A14 FA401WU** |
| **[#148](https://github.com/OpenGamingCollective/asusctl/issues/148)** | [Support] ASUS TUF Gaming A16 (FA608WV) keyboard backli... | `general` | 🟢 **IN PR (#147)** | **PR #147 / branch `lamparray` (commit `2d0b9530`): Support TUF A16 FA608WV HID LampArray** |
| **[#119](https://github.com/OpenGamingCollective/asusctl/issues/119)** | [Feature Request] RGB keyboard support for ASUS TUF Gam... | `general` | 💡 **FEATURE REQUEST** | **Phase 2.4: Add RGB keyboard support for TUF Gaming A18 FA808UM (2025)** |
| **[#123](https://github.com/OpenGamingCollective/asusctl/issues/123)** | G513QY - Loss of separate control of lightbar and keybo... | `general` | ⚠️ **ACTIVE BUG** | **Phase 2.4: Restore discrete LED zone addressing for G513QY lightbar and keyboard** |
| **[#110](https://github.com/OpenGamingCollective/asusctl/issues/110)** | [Feature Request / Bug] ASUS Zenbook Duo 2025 — keyboar... | `general` | 💡 **FEATURE REQUEST** | **Phase 2.4: Add Zenbook Duo 2025 (UX8406) detachable Bluetooth/I2C keyboard backlight support** |
| **[#108](https://github.com/OpenGamingCollective/asusctl/issues/108)** | `platform::cameramute` LED not supported on ASUS Zenboo... | `general` | 💡 **FEATURE REQUEST** | **Phase 2.2: Add cameramute LED sysfs driver binding for Zenbook S 16 UM5606WA** |
| **[#98](https://github.com/OpenGamingCollective/asusctl/issues/98)** | Automatic keyboard backlight timeout and wake-on-input... | `general` | 💡 **FEATURE REQUEST** | **Phase 2.1: Add idle inactivity timer daemon hook to turn off keyboard backlight automatically** |

---

## 5. 🖥️ GUI (`rog-control-center`) & CLI (`asusctl`) Ergonomics

| Issue # | Title | Subsystems | Status / Fix Verification | Architectural Resolution & Roadmap Link |
| :--- | :--- | :--- | :---: | :--- |
| **[#295](https://github.com/OpenGamingCollective/asusctl/issues/295)** | docs: fix the missing ROG Ally and Ally X section in th... | `documentation` | ✅ **RESOLVED UPSTREAM** | **Fixed via PR #303 (commit `5307fd13`): Added Bazzite Ally & Ally X guide** |
| **[#245](https://github.com/OpenGamingCollective/asusctl/issues/245)** | [Feature Request] Take over the AUR PKGBUILD... | `enhancement` | 💡 **FEATURE REQUEST** | **Phase 1.4: Coordinate upstream maintenance of AUR asusctl and asusctl-git packages** |
| **[#198](https://github.com/OpenGamingCollective/asusctl/issues/198)** | The "Advanced" Platform Policy Page closes when clickin... | `general` | ⚠️ **ACTIVE BUG** | **Phase 3.4 (Slint UI): Fix event bubbling in Slint TouchArea widgets across platform tuning sub-pages** |
| **[#193](https://github.com/OpenGamingCollective/asusctl/issues/193)** | [rog-control-center] Proposal: high-fidelity ROG skin —... | `general` | 💡 **FEATURE REQUEST** | **Phase 3.4 (Slint UI): High-fidelity ROG dark/metallic theme & custom asset styling** |
| **[#160](https://github.com/OpenGamingCollective/asusctl/issues/160)** | .deb package building script... | `general` | 💡 **FEATURE REQUEST** | **Phase 4: Maintain standardized cargo-deb workflow in .github/workflows/ and debian/ packaging** |
| **[#89](https://github.com/OpenGamingCollective/asusctl/issues/89)** | Setting in /etc/asusd/asusd.ron not exposed in rog-cont... | `general` | ⚠️ **ACTIVE BUG** | **Phase 3.4: Expose advanced /etc/asusd/asusd.ron settings in Slint GUI settings page** |

---

## 6. 📦 Packaging, Distribution & Ecosystem Integration

| Issue # | Title | Subsystems | Status / Fix Verification | Architectural Resolution & Roadmap Link |
| :--- | :--- | :--- | :---: | :--- |
| **[#131](https://github.com/OpenGamingCollective/asusctl/issues/131)** | Proart H7604JI support... | `general` | 💡 **FEATURE REQUEST** | **Phase 2.4 (dmi-id): Add Asus ProArt Studiobook H7604JI support** |
| **[#130](https://github.com/OpenGamingCollective/asusctl/issues/130)** | Add Asus TUF A14 2025 FA401KM to supported devices... | `general` | 💡 **FEATURE REQUEST** | **Phase 2.4 (dmi-id): Add Asus TUF A14 2025 FA401KM support** |
| **[#124](https://github.com/OpenGamingCollective/asusctl/issues/124)** | PPT data collection thread... | `enhancement`, `rog-platform`, `kernel` | 💡 **FEATURE REQUEST** | **Phase 2.3 & 2.4: Continuous ingestion of verified DMI board names and TDP ranges** |
| **[#107](https://github.com/OpenGamingCollective/asusctl/issues/107)** | Please add support to Asus Tuf Gaming A18... | `general` | 💡 **FEATURE REQUEST** | **Phase 2.4: Add Asus TUF Gaming A18 DMI taxonomy profile** |
| **[#106](https://github.com/OpenGamingCollective/asusctl/issues/106)** | Support Request - Asus Vivobook 14 (TM420ua) ((ryzen 55... | `general` | 💡 **FEATURE REQUEST** | **Phase 2.4: Add Asus Vivobook 14 TM420UA support** |
| **[#103](https://github.com/OpenGamingCollective/asusctl/issues/103)** | nv_temp_target doesnt work on g14 (2023)... | `general` | ⚠️ **ACTIVE BUG** | **Phase 2.2: Validate nv_temp_target sysfs node presence and write permissions on G14 2023** |
| **[#94](https://github.com/OpenGamingCollective/asusctl/issues/94)** | Not booting at startup?... | `general` | ⚠️ **ACTIVE BUG** | **Phase 1.1: Fix systemd unit dependency ordering (After=dbus.service) to guarantee startup** |
| **[#91](https://github.com/OpenGamingCollective/asusctl/issues/91)** | [Feature request] Add panel_overdrive and nv_settings t... | `general` | 💡 **FEATURE REQUEST** | **Phase 2.5: Add panel_overdrive and nv_settings into per-profile config schema** |
| **[#70](https://github.com/OpenGamingCollective/asusctl/issues/70)** | How to add more animations to anime matrix in rog contr... | `general` | 💡 **FEATURE REQUEST** | **Phase 3.2: AniMe Matrix custom GIF/APNG drag-and-drop animation loader in UI** |
| **[#25](https://github.com/OpenGamingCollective/asusctl/issues/25)** | UX8406 (Zenbook Duo 2024) support... | `general` | 💡 **FEATURE REQUEST** | **Phase 2.4: Full support matrix integration for Zenbook Duo 2024 (UX8406)** |

---

## 🔗 Cross References

* Main Architectural Plan: [README.md](README.md)
* Comprehensive Pull Requests Catalog: [PULL_REQUESTS.md](PULL_REQUESTS.md)

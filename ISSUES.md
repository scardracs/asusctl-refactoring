# 🐛 Active Upstream Issues & Roadmap Mapping

> *Last automated synchronization: 2026-08-18 15:57 UTC*

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

| Issue # | Title | Subsystems | Status | Architectural Resolution & Roadmap Link |
| :--- | :--- | :--- | :---: | :--- |
| **[#318](https://github.com/OpenGamingCollective/asusctl/issues/318)** | [Bug]: GPU mode switch via rog-control-center not appli... | `bug`, `rog-control-center`, `asusd` | 🔄 **OPEN** | **Phase 2.1 / 2.2: Normalize kernel sysfs return codes (EEXIST / no-op writes) during shutdown sync.** |
| **[#302](https://github.com/OpenGamingCollective/asusctl/issues/302)** | [Bug]: dGPU still resumed every 2 s on 6.4.0 — #294's g... | `bug`, `rog-control-center`, `rog-platform` | 🔄 **OPEN** | **Phase 1.1 / Section 3.3: Extend zero-wakeup check to inspect entire PCI sub-tree (including GPU Audio 01:00.1).** |
| **[#288](https://github.com/OpenGamingCollective/asusctl/issues/288)** | [Bug]: AniMe Matrix power-state handlers are not starte... | `bug`, `asusd`, `rog-anime` | 🔄 **OPEN** | **Phase 1.1 / PR #317: Dedicated AniMe task lifecycle initialization with power state evaluation.** |
| **[#264](https://github.com/OpenGamingCollective/asusctl/issues/264)** | [Documentation Bug]: Recommend 'systemctl mask' for pow... | `bug`, `documentation`, `rog-profiles` | 🔄 **OPEN** | **Phase 2.5 & Docs: Update distribution setup guides with explicit power-profiles-daemon masking instructions.** |
| **[#250](https://github.com/OpenGamingCollective/asusctl/issues/250)** | Support request: ASUS V16 V3607VM — pwm1/pwm2 fan contr... | `bug`, `enhancement`, `rog-profiles` | 🔄 **OPEN** | **Phase 2.2: Extend rog-platform EC mailbox probe to recognize Vivobook V3607 series EC tables.** |
| **[#204](https://github.com/OpenGamingCollective/asusctl/issues/204)** | FX507ZM: Enabling custom fan curves causes NVIDIA GPU t... | `general` | 🔄 **OPEN** | **Phase 2.2: EC firmware quirk on 2022 TUF models where manual fan tables reset dynamic boost budget.** |
| **[#196](https://github.com/OpenGamingCollective/asusctl/issues/196)** | Fan curves for Quiet profile silently reverted to enabl... | `general` | 🔄 **OPEN** | **Phase 2.5: Preserve user-configured custom curve enable states in daemon memory across ACPI profile switches.** |
| **[#162](https://github.com/OpenGamingCollective/asusctl/issues/162)** | GA401QE: Custom fan curves are not reapplied after AC p... | `general` | 🔄 **OPEN** | **Phase 2.5 / PR #316: Re-apply custom fan curve tables immediately upon logind power source transition events.** |
| **[#153](https://github.com/OpenGamingCollective/asusctl/issues/153)** | Battery charge limit not enforced on ASUS Vivobook 16 V... | `general` | 🔄 **OPEN** | **Phase 2.2: Fallback to /sys/class/power_supply/BAT0/charge_control_end_threshold with direct WMI EC verification.** |
| **[#152](https://github.com/OpenGamingCollective/asusctl/issues/152)** | Boot freeze at Plasma desktop on AC→battery transition,... | `general` | 🔄 **OPEN** | **Phase 1.4 / PR #310: Eliminate asusd-user.service to prevent dual-daemon race conditions and desktop freeze loops.** |
| **[#145](https://github.com/OpenGamingCollective/asusctl/issues/145)** | CPU power limit settings do not take effect (overriden ... | `general` | 🔄 **OPEN** | **Phase 2 / 3: Refactoring roadmap tracking** |
| **[#136](https://github.com/OpenGamingCollective/asusctl/issues/136)** | Fan curves desync from platform profile after boot (bal... | `general` | 🔄 **OPEN** | **Phase 2 / 3: Refactoring roadmap tracking** |
| **[#132](https://github.com/OpenGamingCollective/asusctl/issues/132)** | asusd: one firmware-rejected attribute (nv_dynamic_boos... | `general` | 🔄 **OPEN** | **Phase 2 / 3: Refactoring roadmap tracking** |
| **[#129](https://github.com/OpenGamingCollective/asusctl/issues/129)** | GPU control over iGPU and dGPU lost, with system tray i... | `general` | 🔄 **OPEN** | **Phase 2 / 3: Refactoring roadmap tracking** |
| **[#117](https://github.com/OpenGamingCollective/asusctl/issues/117)** | rog-control-center Charge Limit No Longer Working... | `general` | 🔄 **OPEN** | **Phase 2 / 3: Refactoring roadmap tracking** |
| **[#112](https://github.com/OpenGamingCollective/asusctl/issues/112)** | Fans are not following their profiles after connecting/... | `general` | 🔄 **OPEN** | **Phase 2 / 3: Refactoring roadmap tracking** |
| **[#100](https://github.com/OpenGamingCollective/asusctl/issues/100)** | CPU is heavily power limited (Zephyrus M16 2023)... | `general` | 🔄 **OPEN** | **Phase 2 / 3: Refactoring roadmap tracking** |
| **[#82](https://github.com/OpenGamingCollective/asusctl/issues/82)** | Show OSD notification on power profile change... | `general` | 🔄 **OPEN** | **Phase 2 / 3: Refactoring roadmap tracking** |
| **[#68](https://github.com/OpenGamingCollective/asusctl/issues/68)** | Add Static and BatteryLevel modes for slash lighting... | `general` | 🔄 **OPEN** | **Phase 2 / 3: Refactoring roadmap tracking** |

---

## 2. ⚡ Concurrency, D-Bus Deadlocks & Async Task Lifecycles

| Issue # | Title | Subsystems | Status | Architectural Resolution & Roadmap Link |
| :--- | :--- | :--- | :---: | :--- |
| **[#232](https://github.com/OpenGamingCollective/asusctl/issues/232)** | asusd-user crashes on startup: DBus path mismatch for A... | `general` | 🔄 **OPEN** | **Phase 1.4 / PR #310: Purge asusd-user crate entirely. All clients communicate with asusd system D-Bus paths.** |
| **[#229](https://github.com/OpenGamingCollective/asusctl/issues/229)** | rog-control-center leaks a D-Bus connection per poll an... | `general` | 🔄 **OPEN** | **Phase 1.1 / 'Async Control, Sync Data': Standardize on a single, long-lived zbus::Connection proxy pool.** |

---

## 3. 🛡️ Crashes, Panics & Protocol Robustness (Zero-Unwrap Invariant)

| Issue # | Title | Subsystems | Status | Architectural Resolution & Roadmap Link |
| :--- | :--- | :--- | :---: | :--- |
| **[#304](https://github.com/OpenGamingCollective/asusctl/issues/304)** | [Bug]: rog-control-center panics when config file is re... | `bug`, `rog-control-center` | 🔄 **OPEN** | **Invariant #5 & PR #305: Remove `.unwrap()` in config-traits; fallback gracefully when file is read-only.** |
| **[#159](https://github.com/OpenGamingCollective/asusctl/issues/159)** | rog-control-center panics on GZ302: duplicate entry in ... | `general` | 🔄 **OPEN** | **Phase 2.4 (dmi-id): Deduplicate RON configuration schemas and validate RON files with unit test linters in CI.** |

---

## 4. ⌨️ Hardware Quirks, Keyboard Backlight & DMI Taxonomy Engine

| Issue # | Title | Subsystems | Status | Architectural Resolution & Roadmap Link |
| :--- | :--- | :--- | :---: | :--- |
| **[#284](https://github.com/OpenGamingCollective/asusctl/issues/284)** | [Device Support]: TUF Gaming A18 FA808UM — backlight wo... | `bug`, `enhancement`, `asusd` | 🔄 **OPEN** | **Phase 2.4 (dmi-id) & Phase 2.1: Add LampArray HID transport backend selection in rog-aura when WMI returns 0.** |
| **[#263](https://github.com/OpenGamingCollective/asusctl/issues/263)** | [Device Support]: No keyboard backlight on ASUS TUF Gam... | `bug`, `enhancement`, `asusd` | 🔄 **OPEN** | **Phase 2.4 (dmi-id): Add FA608PP model family quirk mapping to route backlight via standard WMI EC registers.** |
| **[#225](https://github.com/OpenGamingCollective/asusctl/issues/225)** | Add Aura support for ASUS TUF Gaming A16 FA608PP... | `general` | 🔄 **OPEN** | **Phase 2 / 3: Refactoring roadmap tracking** |
| **[#210](https://github.com/OpenGamingCollective/asusctl/issues/210)** | (rog-control-center): App window closes immediately whe... | `general` | 🔄 **OPEN** | **Phase 3.4: Ensure application event loop respects normal window close events rather than terminating on hidden state.** |
| **[#169](https://github.com/OpenGamingCollective/asusctl/issues/169)** | Add Aura support for G614PM (ROG Strix G16)... | `general` | 🔄 **OPEN** | **Phase 2 / 3: Refactoring roadmap tracking** |
| **[#165](https://github.com/OpenGamingCollective/asusctl/issues/165)** | [Flow Z13 2025] External touchpad does not work when ke... | `general` | 🔄 **OPEN** | **Phase 1.1 / 2.1: Maintain SCSI keep-alive polling on tablet base controller even when detachable keyboard disconnects.** |
| **[#151](https://github.com/OpenGamingCollective/asusctl/issues/151)** | Keyboard backlight non-functional on ASUS TUF Gaming A1... | `general` | 🔄 **OPEN** | **Phase 2 / 3: Refactoring roadmap tracking** |
| **[#148](https://github.com/OpenGamingCollective/asusctl/issues/148)** | [Support] ASUS TUF Gaming A16 (FA608WV) keyboard backli... | `general` | 🔄 **OPEN** | **Phase 2 / 3: Refactoring roadmap tracking** |
| **[#119](https://github.com/OpenGamingCollective/asusctl/issues/119)** | [Feature Request] RGB keyboard support for ASUS TUF Gam... | `general` | 🔄 **OPEN** | **Phase 2 / 3: Refactoring roadmap tracking** |
| **[#123](https://github.com/OpenGamingCollective/asusctl/issues/123)** | G513QY - Loss of separate control of lightbar and keybo... | `general` | 🔄 **OPEN** | **Phase 2 / 3: Refactoring roadmap tracking** |
| **[#110](https://github.com/OpenGamingCollective/asusctl/issues/110)** | [Feature Request / Bug] ASUS Zenbook Duo 2025 — keyboar... | `general` | 🔄 **OPEN** | **Phase 2 / 3: Refactoring roadmap tracking** |
| **[#108](https://github.com/OpenGamingCollective/asusctl/issues/108)** | `platform::cameramute` LED not supported on ASUS Zenboo... | `general` | 🔄 **OPEN** | **Phase 2 / 3: Refactoring roadmap tracking** |
| **[#98](https://github.com/OpenGamingCollective/asusctl/issues/98)** | Automatic keyboard backlight timeout and wake-on-input... | `general` | 🔄 **OPEN** | **Phase 2 / 3: Refactoring roadmap tracking** |

---

## 5. 🖥️ GUI (`rog-control-center`) & CLI (`asusctl`) Ergonomics

| Issue # | Title | Subsystems | Status | Architectural Resolution & Roadmap Link |
| :--- | :--- | :--- | :---: | :--- |
| **[#295](https://github.com/OpenGamingCollective/asusctl/issues/295)** | docs: fix the missing ROG Ally and Ally X section in th... | `documentation` | 🔄 **OPEN** | **Docs: Document Handheld daemon integration and Bazzite ujust automation.** |
| **[#245](https://github.com/OpenGamingCollective/asusctl/issues/245)** | [Feature Request] Take over the AUR PKGBUILD... | `enhancement` | 🔄 **OPEN** | **Phase 1.4: Coordinate upstream maintenance of AUR asusctl and asusctl-git packages with cleanup_asusd_leftovers.** |
| **[#198](https://github.com/OpenGamingCollective/asusctl/issues/198)** | The "Advanced" Platform Policy Page closes when clickin... | `general` | 🔄 **OPEN** | **Phase 3.4 (Slint UI): Fix event bubbling in Slint TouchArea widgets across platform tuning sub-pages.** |
| **[#193](https://github.com/OpenGamingCollective/asusctl/issues/193)** | [rog-control-center] Proposal: high-fidelity ROG skin —... | `general` | 🔄 **OPEN** | **Phase 2 / 3: Refactoring roadmap tracking** |
| **[#160](https://github.com/OpenGamingCollective/asusctl/issues/160)** | .deb package building script... | `general` | 🔄 **OPEN** | **Phase 2 / 3: Refactoring roadmap tracking** |
| **[#89](https://github.com/OpenGamingCollective/asusctl/issues/89)** | Setting in /etc/asusd/asusd.ron not exposed in rog-cont... | `general` | 🔄 **OPEN** | **Phase 2 / 3: Refactoring roadmap tracking** |

---

## 6. 📦 Packaging, Distribution & Ecosystem Integration

| Issue # | Title | Subsystems | Status | Architectural Resolution & Roadmap Link |
| :--- | :--- | :--- | :---: | :--- |
| **[#131](https://github.com/OpenGamingCollective/asusctl/issues/131)** | Proart H7604JI support... | `general` | 🔄 **OPEN** | **Phase 2 / 3: Refactoring roadmap tracking** |
| **[#130](https://github.com/OpenGamingCollective/asusctl/issues/130)** | Add Asus TUF A14 2025 FA401KM to supported devices... | `general` | 🔄 **OPEN** | **Phase 2 / 3: Refactoring roadmap tracking** |
| **[#124](https://github.com/OpenGamingCollective/asusctl/issues/124)** | PPT data collection thread... | `enhancement`, `rog-platform`, `kernel` | 🔄 **OPEN** | **Phase 2 / 3: Refactoring roadmap tracking** |
| **[#107](https://github.com/OpenGamingCollective/asusctl/issues/107)** | Please add support to Asus Tuf Gaming A18... | `general` | 🔄 **OPEN** | **Phase 2 / 3: Refactoring roadmap tracking** |
| **[#106](https://github.com/OpenGamingCollective/asusctl/issues/106)** | Support Request - Asus Vivobook 14 (TM420ua) ((ryzen 55... | `general` | 🔄 **OPEN** | **Phase 2 / 3: Refactoring roadmap tracking** |
| **[#103](https://github.com/OpenGamingCollective/asusctl/issues/103)** | nv_temp_target doesnt work on g14 (2023)... | `general` | 🔄 **OPEN** | **Phase 2 / 3: Refactoring roadmap tracking** |
| **[#94](https://github.com/OpenGamingCollective/asusctl/issues/94)** | Not booting at startup?... | `general` | 🔄 **OPEN** | **Phase 2 / 3: Refactoring roadmap tracking** |
| **[#91](https://github.com/OpenGamingCollective/asusctl/issues/91)** | [Feature request] Add panel_overdrive and nv_settings t... | `general` | 🔄 **OPEN** | **Phase 2 / 3: Refactoring roadmap tracking** |
| **[#70](https://github.com/OpenGamingCollective/asusctl/issues/70)** | How to add more animations to anime matrix in rog contr... | `general` | 🔄 **OPEN** | **Phase 2 / 3: Refactoring roadmap tracking** |
| **[#25](https://github.com/OpenGamingCollective/asusctl/issues/25)** | UX8406 (Zenbook Duo 2024) support... | `general` | 🔄 **OPEN** | **Phase 2 / 3: Refactoring roadmap tracking** |

---

## 🔗 Cross References

* Main Architectural Plan: [README.md](README.md)
* Comprehensive Pull Requests Catalog: [PULL_REQUESTS.md](PULL_REQUESTS.md)

# 🐛 Upstream Issues Audit & Roadmap Mapping

This document provides a comprehensive analysis of all open issues and key resolved issues from [`OpenGamingCollective/asusctl/issues`](https://github.com/OpenGamingCollective/asusctl/issues).

Issues are categorized by subsystem and functional domain, detailing their root causes and mapping them directly to our architectural refactoring roadmap, pull requests, and engineering invariants.

---

## 📑 Issue Category Index

1. [🔋 Power Management, GPU Switching & Zero-Wakeup Telemetry](#1--power-management-gpu-switching--zero-wakeup-telemetry)
2. [⚡ Concurrency, D-Bus Deadlocks & Async Task Lifecycles](#2--concurrency-d-bus-deadlocks--async-task-lifecycles)
3. [🛡️ Crashes, Panics & Protocol Robustness (Zero-Unwrap Invariant)](#3-️-crashes-panics--protocol-robustness-zero-unwrap-invariant)
4. [⌨️ Hardware Quirks, Keyboard Backlight & DMI Taxonomy Engine](#4-️-hardware-quirks-keyboard-backlight--dmi-taxonomy-engine)
5. [🖥️ GUI (`rog-control-center`) & CLI (`asusctl`) Ergonomics](#5-️-gui-rog-control-center--cli-asusctl-ergonomics)
6. [📦 Packaging, Distribution & Ecosystem Integration](#6--packaging-distribution--ecosystem-integration)

---

## 1. 🔋 Power Management, GPU Switching & Zero-Wakeup Telemetry

| Issue # | Title | Subsystems | Status | Architectural Resolution & Roadmap Link |
| :--- | :--- | :--- | :---: | :--- |
| **[#318](https://github.com/OpenGamingCollective/asusctl/issues/318)** | GPU mode switch via `rog-control-center` not applied after reboot (`asus-shutdown` aborts on no-op `dgpu_disable` write) | `asusd`, `rog-platform`, `kernel` | 🔄 **OPEN** | **Phase 2.1 / 2.2**: Normalize kernel sysfs return codes (`EEXIST` / no-op writes) during shutdown sync; make state transition commits resilient against no-op errors. |
| **[#302](https://github.com/OpenGamingCollective/asusctl/issues/302)** | dGPU still resumed every 2s on 6.4.0 — guard bypassed via sibling audio PCI function, and iGPU telemetry reports dGPU | `rog-platform`, `rog-control-center` | 🔄 **OPEN** | **Phase 1.1 / Section 3.3**: Extend zero-wakeup check to inspect the entire PCI sub-tree (including GPU High Definition Audio Controller `01:00.1`) before sampling telemetry. |
| **[#293](https://github.com/OpenGamingCollective/asusctl/issues/293)** | `rog-control-center` telemetry loop calls NVML unconditionally, waking runtime-suspended dGPU | `rog-control-center`, `rog-platform` | ✅ **CLOSED** | **Resolved via PR #294**: Eliminated unconditional NVML calls; added passive sysfs power-state checks (`runtime_status`). |
| **[#234](https://github.com/OpenGamingCollective/asusctl/issues/234)** / **[#208](https://github.com/OpenGamingCollective/asusctl/issues/208)** / **[#231](https://github.com/OpenGamingCollective/asusctl/issues/231)** | `rog-control-center` keeps dGPU permanently alive while tray icon is active | `asusd`, `rog-control-center` | ✅ **CLOSED** | **Resolved via PR #294**: Deduplicated udev scans, removed process polling (`lspci`), and guarded telemetry polling. |
| **[#162](https://github.com/OpenGamingCollective/asusctl/issues/162)** | GA401QE: Custom fan curves not reapplied after AC power events | `rog-profiles`, `asusd` | 🔄 **OPEN** | **Phase 2.5 / PR #316**: Re-apply custom fan curve tables and platform profile states immediately upon `logind` power source transition events. |
| **[#196](https://github.com/OpenGamingCollective/asusctl/issues/196)** | Fan curves for Quiet profile silently reverted to `enabled:false` on profile switch/suspend | `rog-profiles`, `asusd` | 🔄 **OPEN** | **Phase 2.5**: Preserve user-configured custom curve enable states in daemon memory across ACPI platform profile switches. |
| **[#204](https://github.com/OpenGamingCollective/asusctl/issues/204)** | FX507ZM: Enabling custom fan curves causes NVIDIA GPU to become software power capped (~90W → ~30W) | `rog-profiles`, `kernel` | 🔄 **OPEN** | **Phase 2.2**: EC firmware quirk on 2022 TUF models where manual fan tables reset the dynamic boost thermal budget. Documented and bypassed via Armoury TGP override. |
| **[#205](https://github.com/OpenGamingCollective/asusctl/issues/205)** | No warning when `power-profiles-daemon` (PPD) is active — PPD contention silently resets EPP | `asusd`, `docs` | ✅ **CLOSED** | **Phase 2.5 & Docs**: Added conflict detection and guidance recommending `systemctl mask power-profiles-daemon`. |
| **[#153](https://github.com/OpenGamingCollective/asusctl/issues/153)** | Battery charge limit not enforced on Vivobook 16 V3607VU | `rog-platform`, `kernel` | 🔄 **OPEN** | **Phase 2.2**: Fallback to `/sys/class/power_supply/BAT0/charge_control_end_threshold` with direct WMI EC verification. |

---

## 2. ⚡ Concurrency, D-Bus Deadlocks & Async Task Lifecycles

| Issue # | Title | Subsystems | Status | Architectural Resolution & Roadmap Link |
| :--- | :--- | :--- | :---: | :--- |
| **[#229](https://github.com/OpenGamingCollective/asusctl/issues/229)** | `rog-control-center` leaks a D-Bus connection per poll and panics after ~12 minutes | `rog-control-center`, `rog-dbus` | 🔄 **OPEN** | **Phase 1.1 / "Async Control, Sync Data"**: Standardize on a single, long-lived `zbus::Connection` proxy pool; eliminate ad-hoc connection creation inside telemetry intervals. |
| **[#235](https://github.com/OpenGamingCollective/asusctl/issues/235)** | `asusd` seems to be overloading `systemd-logind` | `asusd` | ✅ **CLOSED** | **Resolved via PR #297**: Replaced high-frequency polling loops with event-driven `logind-zbus` signals (`PrepareForSleep`, `PropertiesChanged`). |
| **[#260](https://github.com/OpenGamingCollective/asusctl/issues/260)** | `rog-control-center` keeps a stale Aura proxy after keyboard hotplug | `rog-control-center`, `rog-aura` | ✅ **CLOSED** | **Phase 3.3 (`tokio-udev`)**: Re-instantiate UI D-Bus proxies reactively upon receiving udev device removal/addition notifications. |
| **[#259](https://github.com/OpenGamingCollective/asusctl/issues/259)** | `asusd`: Keyboard LEDs stay dark after detachable keyboard is reattached | `asusd`, `rog-aura` | ✅ **CLOSED** | **Phase 3.3 (`tokio-udev`)**: Dynamic re-enumeration and effect state re-application upon USB HID add events. |
| **[#258](https://github.com/OpenGamingCollective/asusctl/issues/258)** | `rog-control-center` binds to a random Aura device when laptop exposes multiple controllers | `rog-control-center`, `rog-aura` | ✅ **CLOSED** | **Phase 2.4 (`dmi-id`)**: Deterministic priority binding for primary internal keyboards over secondary RGB peripherals. |
| **[#288](https://github.com/OpenGamingCollective/asusctl/issues/288)** | AniMe Matrix power-state handlers are not started since 6.1 | `asusd`, `rog-anime` | 🔄 **OPEN** | **Phase 1.1 / PR #317**: Dedicated AniMe task lifecycle initialization with power state evaluation and zero-copy proxy. |

---

## 3. 🛡️ Crashes, Panics & Protocol Robustness (Zero-Unwrap Invariant)

| Issue # | Title | Subsystems | Status | Architectural Resolution & Roadmap Link |
| :--- | :--- | :--- | :---: | :--- |
| **[#304](https://github.com/OpenGamingCollective/asusctl/issues/304)** | `rog-control-center` panics when config file is read-only | `rog-control-center`, `config-traits` | 🔄 **OPEN** | **Invariant #5 & PR #305**: Remove `.unwrap()` in `config-traits`; fallback to default in-memory configuration with non-fatal logging when file is read-only. |
| **[#232](https://github.com/OpenGamingCollective/asusctl/issues/232)** | `asusd-user` crashes on startup: DBus path mismatch for Aura interface | `asusd-user`, `rog-dbus` | 🔄 **OPEN** | **Phase 1.4 / PR #310**: **Purge `asusd-user` crate entirely**. All clients communicate with `asusd` system D-Bus paths. |
| **[#152](https://github.com/OpenGamingCollective/asusctl/issues/152)** | Boot freeze at Plasma desktop on AC→battery transition (`asusd-user` crash loops) | `asusd-user`, `rog-platform` | 🔄 **OPEN** | **Phase 1.4 / PR #310**: Eliminate `asusd-user.service` to prevent dual-daemon race conditions and desktop freeze loops. |
| **[#159](https://github.com/OpenGamingCollective/asusctl/issues/159)** | `rog-control-center` panics on GZ302: duplicate entry in `aura_support.ron` | `rog-control-center`, `rog-aura` | 🔄 **OPEN** | **Phase 2.4 (`dmi-id`)**: Deduplicate RON configuration schemas and validate RON files with unit test linters in CI. |
| **[#213](https://github.com/OpenGamingCollective/asusctl/issues/213)** | `rog-control-center` runtime startup crash | `rog-control-center` | ✅ **CLOSED** | **Resolved via PR #306**: Eliminated nested Tokio runtime construction (`Runtime::new()`) inside UI thread. |

---

## 4. ⌨️ Hardware Quirks, Keyboard Backlight & DMI Taxonomy Engine

| Issue # | Title | Subsystems | Status | Architectural Resolution & Roadmap Link |
| :--- | :--- | :--- | :---: | :--- |
| **[#284](https://github.com/OpenGamingCollective/asusctl/issues/284)** | TUF Gaming A18 FA808UM: Backlight works via HID LampArray on I2C-HID (WMI path inert) | `asusd`, `rog-aura`, `kernel` | 🔄 **OPEN** | **Phase 2.4 (`dmi-id`) & Phase 2.1**: Add LampArray HID transport backend selection in `rog-aura` when WMI `DSTS` returns `0`. |
| **[#263](https://github.com/OpenGamingCollective/asusctl/issues/263)** / **[#225](https://github.com/OpenGamingCollective/asusctl/issues/225)** | No keyboard backlight on TUF Gaming A16 FA608PP | `asusd`, `rog-aura` | 🔄 **OPEN** | **Phase 2.4 (`dmi-id`)**: Add FA608PP model family quirk mapping to route backlight via standard WMI EC registers. |
| **[#250](https://github.com/OpenGamingCollective/asusctl/issues/250)** | ASUS V16 V3607VM: Fan control missing (RFOV/WFOV EC mailbox confirmed working) | `rog-platform`, `rog-profiles` | 🔄 **OPEN** | **Phase 2.2**: Extend `rog-platform` EC mailbox probe to recognize Vivobook V3607 series EC tables. |
| **[#165](https://github.com/OpenGamingCollective/asusctl/issues/165)** | Flow Z13 2025: External touchpad does not work when detachable keyboard is disconnected | `asusd`, `rog-scsi` | 🔄 **OPEN** | **Phase 1.1 / 2.1**: Maintain SCSI keep-alive polling on tablet base controller even when primary keyboard detachment event fires. |
| **[#255](https://github.com/OpenGamingCollective/asusctl/issues/255)** | Rainbow effect available on Flow Z13 (GZ301Z) but disabled in `asusctl` | `rog-aura`, `rog-control-center` | ✅ **CLOSED** | **Phase 3.4 (`bitflags`)**: Strongly-typed capability flags unlock full hardware effect matrices on supported single-zone ROG devices. |
| **[#286](https://github.com/OpenGamingCollective/asusctl/issues/286)** / **[#267](https://github.com/OpenGamingCollective/asusctl/issues/267)** / **[#307](https://github.com/OpenGamingCollective/asusctl/issues/307)** | Add Aura support for FA706IC, Tianxuan 6 Pro FA608FM, Strix G16 G614PP | `rog-aura` | ✅ **CLOSED** | **Resolved**: Model capability tables updated and merged upstream. |
| **[#124](https://github.com/OpenGamingCollective/asusctl/issues/124)** | PPT & Power Limit data collection thread across ASUS laptop models | `rog-platform`, `asus-armoury` | 🔄 **OPEN** | **Phase 2.3 & 2.4**: Continuous ingestion of verified DMI board names and TDP ranges into `dmi-id` and `asus-armoury` tables. |

---

## 5. 🖥️ GUI (`rog-control-center`) & CLI (`asusctl`) Ergonomics

| Issue # | Title | Subsystems | Status | Architectural Resolution & Roadmap Link |
| :--- | :--- | :--- | :---: | :--- |
| **[#210](https://github.com/OpenGamingCollective/asusctl/issues/210)** | App window closes immediately when both `run_in_background` and global shortcuts are disabled | `rog-control-center` | 🔄 **OPEN** | **Phase 3.4**: Ensure application event loop respects normal window close events rather than terminating process on hidden state. |
| **[#198](https://github.com/OpenGamingCollective/asusctl/issues/198)** | "Advanced" Platform Policy Page closes when clicking text or blank space | `rog-control-center` | 🔄 **OPEN** | **Phase 3.4 (Slint UI)**: Fix event bubbling in Slint `TouchArea` widgets across platform tuning sub-pages. |
| **[#254](https://github.com/OpenGamingCollective/asusctl/issues/254)** | Sidebar navigation items overlap in `rog-control-center` | `rog-control-center` | ✅ **CLOSED** | **Resolved via PR #315 / #279**: Window minimum size adjustments and responsive layout constraints in `rog.slint`. |
| **[#312](https://github.com/OpenGamingCollective/asusctl/issues/312)** | Global shortcuts lost after suspend/resume cycle | `rog-control-center` | 🔄 **OPEN** | **PR #312 / Phase 3.3**: Re-arms XDG Desktop Portal shortcut session upon system resume signals from `logind`. |
| **[#296](https://github.com/OpenGamingCollective/asusctl/issues/296)** | Need user-friendly crash dialogs instead of raw terminal stacktraces | `asusctl`, `rog-control-center` | ⏹️ **CLOSED** | **Phase 3.4 / PR #296**: Reopen PR #296 to integrate `human-panic` across all workspace binaries. |

---

## 6. 📦 Packaging, Distribution & Ecosystem Integration

| Issue # | Title | Subsystems | Status | Architectural Resolution & Roadmap Link |
| :--- | :--- | :--- | :---: | :--- |
| **[#245](https://github.com/OpenGamingCollective/asusctl/issues/245)** | Take over the Arch Linux AUR `asusctl` PKGBUILD | Packaging | 🔄 **OPEN** | **Phase 1.4**: Coordinate upstream maintenance of AUR `asusctl` and `asusctl-git` packages with clean upgrade scripts (`cleanup_asusd_leftovers`). |
| **[#160](https://github.com/OpenGamingCollective/asusctl/issues/160)** | Debian / Ubuntu packaging scripts | Packaging | 🔄 **OPEN** | **Phase 4**: Maintain standardized `cargo-deb` workflow in `.github/workflows/` and Debian packaging files. |
| **[#264](https://github.com/OpenGamingCollective/asusctl/issues/264)** | Recommend `systemctl mask power-profiles-daemon` for KDE Plasma (PowerDevil DBus activation) | Docs, `rog-profiles` | 🔄 **OPEN** | **Phase 2.5 & Docs**: Update distribution setup guides with explicit masking instructions to prevent D-Bus auto-activation. |
| **[#295](https://github.com/OpenGamingCollective/asusctl/issues/295)** | Add missing ROG Ally & Ally X instructions in Bazzite guide | Docs | 🔄 **OPEN** | **Docs**: Document Handheld daemon integration and Bazzite ujust automation. |

---

## 🔗 Cross References

* Main Architectural Plan: [README.md](README.md)
* Comprehensive Pull Requests Catalog: [PULL_REQUESTS.md](PULL_REQUESTS.md)

# 🔀 Active Pull Request Catalog & Architectural Assessment

> *Last automated synchronization: 2026-08-18 16:13 UTC*

This document provides an automated audit of active and actionable upstream pull requests from [`OpenGamingCollective/asusctl`](https://github.com/OpenGamingCollective/asusctl/pulls).

Each pull request is evaluated for its architectural impact, alignment with the **"Async Control, Sync Data"** paradigm, dependency health, and whether it should be merged, kept, or reopened.

---

## 📑 Summary Matrix (Active & Actionable PRs)

| PR # | Type / Area | Branch / Scope | Status | Recommended Action | Roadmap Phase |
| :--- | :--- | :--- | :---: | :--- | :---: |
| **[#317](https://github.com/OpenGamingCollective/asusctl/pull/317)** | `perf(anime): decouple kernel I/O with Co...` | `perf/anime-io-pipeline` | 🔄 **OPEN** | **🟢 KEEP / MERGE: Reference implementation for 'Async Control, Sync Data'** | Phase 1.1 |
| **[#316](https://github.com/OpenGamingCollective/asusctl/pull/316)** | `feat(asusd): remember platform profile p...` | `feat(asusd)/remember-plateform-profile-per-source` | 🔄 **OPEN** | **🟢 KEEP / MERGE: Dynamic AC vs Battery platform profile memory** | Phase 2.5 |
| **[#314](https://github.com/OpenGamingCollective/asusctl/pull/314)** | `refactor: unify image and animation deco...` | `refactor/unify-image-crate` | 🔄 **OPEN** | **🟢 KEEP / MERGE: Consolidated image pipeline under image = '=0.25.9'** | Phase 3.2 |
| **[#312](https://github.com/OpenGamingCollective/asusctl/pull/312)** | `fix(rog-control-center): re-arm global s...` | `fix/global-shortcuts-multi-backend` | 🔄 **OPEN** | **🟢 KEEP / MERGE: Re-arms XDG Global Shortcuts portal upon desktop resume** | Phase 3.3 |
| **[#311](https://github.com/OpenGamingCollective/asusctl/pull/311)** | `chore(asusctl): remove obsolete examples...` | `chore/remove-asusctl-examples` | ⏹️ **CLOSED** | **🟠 REOPEN / MERGE: Purges legacy examples and unneeded check/test targets** | Phase 3.4 |
| **[#310](https://github.com/OpenGamingCollective/asusctl/pull/310)** | `refactor: remove obsolete asusd-user cra...` | `refactor/remove-asusd-user` | ⏹️ **CLOSED** | **🟠 REOPEN / MERGE: Purges obsolete asusd-user crate, units, and packaging bloat** | Phase 1.4 |
| **[#305](https://github.com/OpenGamingCollective/asusctl/pull/305)** | `fix(config-traits): open read-only confi...` | `fix-readonly-config-open` | 🔄 **OPEN** | **🟢 KEEP / MERGE: Prevents panics on read-only configs (Invariant #5)** | Phase 3.4 |
| **[#301](https://github.com/OpenGamingCollective/asusctl/pull/301)** | `refactor(asusd): simplify armoury attrib...` | `refactor/armoury-attribute-persistence` | 🔄 **OPEN** | **🟢 KEEP / MERGE: Simplifies Armoury attribute persistence & boot restoration** | Phase 2.3 |
| **[#300](https://github.com/OpenGamingCollective/asusctl/pull/300)** | `fix(asusd): prevent storing and applying...` | `fix/armoury-unapplicable-tuning-values` | 🔄 **OPEN** | **🟢 KEEP / MERGE: Rejects out-of-bounds Armoury tuning writes to sysfs** | Phase 2.3 |
| **[#296](https://github.com/OpenGamingCollective/asusctl/pull/296)** | `feat: add human panic basic functions...` | `feature/human-panic` | ⏹️ **CLOSED** | **🟠 REOPEN / MERGE: User-friendly crash dialogs & sanitized logs across CLI/GUI** | Phase 3.4 |
| **[#280](https://github.com/OpenGamingCollective/asusctl/pull/280)** | `fix: platform profile handling when quie...` | `fix/platform-profile-cycle-and-epp` | 🔄 **OPEN** | **🟢 KEEP / MERGE: Graceful fallback when firmware lacks Quiet/Low-Power profile** | Phase 2.5 |
| **[#202](https://github.com/OpenGamingCollective/asusctl/pull/202)** | `chore: Setup AI agent infrastructure...` | `feat/ai-agent-infrastructure` | 🔄 **OPEN** | **Evaluate for roadmap integration** | Phase 2 / 3 |

---

## 🔍 Detailed Analysis of Critical Pull Requests

### 1. PR #317: AniMe Kernel I/O Decoupling & Zero-Copy Proxy
* **Scope**: `asusd::aura_anime`, `rog-anime`, `rog-dbus`
* **Branch**: `perf/anime-io-pipeline`
* **Status**: 🔄 Open (Active development)
* **Architectural Value**:
  * Decouples synchronous, blocking USB HID packet writes (`rusb` / `/dev/hidraw`) from Tokio's async reactor via a dedicated OS thread and an `Arc<Condvar>` single-slot mailbox.
  * Replaces expensive D-Bus payload clones with zero-copy `&AnimeDataBuffer` IPC methods in `rog-dbus`.
  * Pre-computes frame diagonals off the event loop, eliminating D-Bus request timeouts and desktop stutter during intensive AniMe Matrix playback.
* **Recommendation**: **🟢 Merge Immediately** as the reference pattern for all hardware controllers.

---

### 2. PR #310: Remove Obsolete `asusd-user` Crate & Services
* **Scope**: Workspace root, `asusd-user/`, `data/asusd-user.service`, `Makefile`, `PKGBUILD`
* **Branch**: `refactor/remove-asusd-user`
* **Status**: ⏹️ Closed without merge (Closed temporarily during Rust 1.85 migration)
* **Architectural Value**:
  * `asusd-user` is redundant: all features (Aura, AniMe, Armoury, fan curves) are natively served on the system D-Bus by `asusd`.
  * All active clients (`asusctl`, `rog-control-center`, desktop extensions) connect solely to the system bus.
  * Dual daemons cause significant user confusion and packaging headaches across Arch, Fedora, Debian, and Ubuntu.
* **Recommendation**: **🟠 Reopen & Merge**. Includes packaging cleanup hooks (`cleanup_asusd_leftovers`) to remove legacy user services upon package upgrade.

---

### 3. PR #314: Unified Image & Animation Decoding Pipeline
* **Scope**: `rog-anime`, `asusctl`, workspace `Cargo.toml`
* **Branch**: `refactor/unify-image-crate`
* **Status**: 🔄 Open
* **Architectural Value**:
  * Purges 4 redundant crates: `png_pong`, `pix`, standalone `gif`, and standalone `png`.
  * Standardizes image and animation decoding under `image = "=0.25.9"`.
  * Fixes subframe canvas coordinate conversion regressions for animated GIF and APNG frames.
* **Recommendation**: **🟢 Merge Immediately**.

---

### 4. PR #316: Platform Profile Memory Per Power Source (AC vs Battery)
* **Scope**: `asusd`, `rog-profiles`, `rog-platform`
* **Branch**: `feature/profile-per-source`
* **Status**: 🔄 Open
* **Architectural Value**:
  * Solves a long-standing user request: allows setting 'Performance' when plugged into AC and 'Quiet' when running on Battery.
  * Automatically switches between remembered profiles upon receiving power supply transition signals from `logind-zbus`.
* **Recommendation**: **🟢 Merge**.

---

### 5. PR #300 & PR #301: Armoury Tuning Validation & Simplified Persistence
* **Scope**: `asusd`, `rog-platform`
* **Branches**: `fix/armoury-tuning-validation`, `refactor/armoury-persistence`
* **Status**: 🔄 Open
* **Architectural Value**:
  * **PR #300**: Validates Armoury attribute values against hardware bounds before writing to sysfs, preventing crashes on unsupported tunables.
  * **PR #301**: Normalizes JSON state serialization in `/var/lib/asusd/armoury.json` with self-healing fallback when loading configs on newly updated kernels.
* **Recommendation**: **🟢 Merge Both** in sequence.

---

### 6. PR #305: Safe Configuration Loading Without Panicking
* **Scope**: `config-traits`
* **Branch**: `fix/config-traits-read-only`
* **Status**: 🔄 Open
* **Architectural Value**:
  * Fixes Issue #304. Prevents `.unwrap()` crashes when configuration files are accessed with read-only permissions or in restricted container environments.
* **Recommendation**: **🟢 Merge**. Enforces Engineering Invariant #5 (Zero `.unwrap()`).

---

### 7. PR #296: Integrated Crash Reporting with `human-panic`
* **Scope**: `asusctl`, `rog-control-center`, `asusd`
* **Branch**: `feature/human-panic`
* **Status**: ⏹️ Closed
* **Architectural Value**:
  * Intercepts unhandled panics across CLI and GUI tools to display clear, actionable crash dialogs and generate sanitized crash report files for bug reporting.
* **Recommendation**: **🟠 Reopen & Merge**.

---

### 8. PR #311: Purge Obsolete Examples & Dev-Dependencies
* **Scope**: `asusctl/examples/`, `asusctl/Cargo.toml`
* **Branch**: `chore/remove-asusctl-examples`
* **Status**: ⏹️ Closed
* **Architectural Value**:
  * Removes outdated example scripts referencing legacy `png` dependencies, reducing compilation time and clutter in `cargo test --all-targets`.
* **Recommendation**: **🟠 Reopen & Merge**.

---

## 🔗 Cross References

* Main Architectural Plan: [README.md](README.md)
* Comprehensive Issues Audit: [ISSUES.md](ISSUES.md)

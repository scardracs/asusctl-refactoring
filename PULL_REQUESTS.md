# 🔀 Pull Request Catalog & Architectural Assessment

This document provides a comprehensive audit of all upstream pull requests (Open, Merged, and Closed-without-merge) for [`OpenGamingCollective/asusctl`](https://github.com/OpenGamingCollective/asusctl/pulls).

Each pull request is evaluated for its architectural impact, alignment with the **"Async Control, Sync Data"** paradigm, dependency health, and whether it should be merged, kept, or reopened.

---

## 📑 Summary Matrix

| PR # | Type / Area | Branch / Scope | Status | Recommended Action | Roadmap Phase |
| :--- | :--- | :--- | :---: | :--- | :---: |
| **[#317](https://github.com/OpenGamingCollective/asusctl/pull/317)** | `perf(anime)` | `perf/anime-io-pipeline` | 🔄 **OPEN** | **🟢 KEEP / MERGE**: Reference implementation for "Async Control, Sync Data". | Phase 1.1 |
| **[#316](https://github.com/OpenGamingCollective/asusctl/pull/316)** | `feat(asusd)` | `feature/profile-per-source` | 🔄 **OPEN** | **🟢 KEEP / MERGE**: Dynamic AC vs Battery platform profile memory. | Phase 2.5 |
| **[#314](https://github.com/OpenGamingCollective/asusctl/pull/314)** | `refactor` | `refactor/unify-image-crate` | 🔄 **OPEN** | **🟢 KEEP / MERGE**: Consolidated image pipeline under `image = "=0.25.9"`. | Phase 3.2 |
| **[#312](https://github.com/OpenGamingCollective/asusctl/pull/312)** | `fix(rogcc)` | `fix/global-shortcuts-bind` | 🔄 **OPEN** | **🟢 KEEP / MERGE**: Re-arms XDG Global Shortcuts portal upon desktop resume. | Phase 3.3 |
| **[#310](https://github.com/OpenGamingCollective/asusctl/pull/310)** | `refactor` | `refactor/remove-asusd-user` | ⏹️ **CLOSED** | **🟠 REOPEN / MERGE**: Purges obsolete `asusd-user` crate, units, and packaging bloat. | Phase 1.4 |
| **[#311](https://github.com/OpenGamingCollective/asusctl/pull/311)** | `chore` | `chore/remove-asusctl-examples` | ⏹️ **CLOSED** | **🟠 REOPEN / MERGE**: Purges legacy examples and unneeded check/test targets. | Phase 3.4 |
| **[#305](https://github.com/OpenGamingCollective/asusctl/pull/305)** | `fix(traits)` | `fix/config-traits-read-only` | 🔄 **OPEN** | **🟢 KEEP / MERGE**: Prevents panics on read-only configs (Invariant #5). | Phase 3.4 |
| **[#301](https://github.com/OpenGamingCollective/asusctl/pull/301)** | `refactor(asusd)` | `refactor/armoury-persistence` | 🔄 **OPEN** | **🟢 KEEP / MERGE**: Simplifies Armoury attribute persistence & boot restoration. | Phase 2.3 |
| **[#300](https://github.com/OpenGamingCollective/asusctl/pull/300)** | `fix(asusd)` | `fix/armoury-tuning-validation` | 🔄 **OPEN** | **🟢 KEEP / MERGE**: Rejects out-of-bounds Armoury tuning writes to sysfs. | Phase 2.3 |
| **[#296](https://github.com/OpenGamingCollective/asusctl/pull/296)** | `feat` | `feature/human-panic` | ⏹️ **CLOSED** | **🟠 REOPEN / MERGE**: User-friendly crash dialogs & sanitized crash logs across CLI/GUI. | Phase 3.4 |
| **[#280](https://github.com/OpenGamingCollective/asusctl/pull/280)** | `fix` | `fix/platform-profile-fallback` | 🔄 **OPEN** | **🟢 KEEP / MERGE**: Graceful fallback when firmware lacks Quiet/Low-Power profile. | Phase 2.5 |
| **[#315](https://github.com/OpenGamingCollective/asusctl/pull/315)** | `refactor(rogcc)` | `clean-and-setup-base` | ✅ **MERGED** | **Merged into `rogcc-redesign`**: Prepares modular pages & accessibility. | Phase 3.4 |
| **[#309](https://github.com/OpenGamingCollective/asusctl/pull/309)** | `chore` | `chore/edition-2024` | ✅ **MERGED** | **Integrated Upstream (`6b6cdc63`)**: Migrated workspace to Rust Edition 2024. | Phase 0.2 |
| **[#308](https://github.com/OpenGamingCollective/asusctl/pull/308)** | `chore` | `chore/bump-rust-1.85` | ✅ **MERGED** | **Integrated Upstream (`84645b6a`)**: Upgraded MSRV to Rust 1.85.0. | Phase 0.2 |
| **[#307](https://github.com/OpenGamingCollective/asusctl/pull/307)** | `feat(aura)` | `feat/g614pp-aura` | ✅ **MERGED** | **Integrated Upstream (`a1322ff9`)**: Added Aura support for ROG Strix G16 G614PP. | Phase 2.4 |
| **[#306](https://github.com/OpenGamingCollective/asusctl/pull/306)** | `fix(rogcc)` | `fix/rogcc-startup-panic` | ✅ **MERGED** | **Integrated Upstream (`31635a6f`)**: Eliminated nested Tokio runtime startup panics. | Phase 1.1 |
| **[#303](https://github.com/OpenGamingCollective/asusctl/pull/303)** | `docs` | `docs/re-structure` | ✅ **MERGED** | **Integrated Upstream (`5307fd13`)**: Major documentation overhaul & CLI guide. | Phase 4 |
| **[#299](https://github.com/OpenGamingCollective/asusctl/pull/299)** | `fix(rogcc)` | `fix/global-shortcuts-lifecycle` | ✅ **MERGED** | **Integrated Upstream (`48daeaab`)**: Adapted XDG shortcuts to KDE portal lifecycle. | Phase 3.3 |
| **[#298](https://github.com/OpenGamingCollective/asusctl/pull/298)** | `chore` | `chore/reinstate-lockfile` | ✅ **MERGED** | **Integrated Upstream (`dfe4185b`)**: Reinstated committed `Cargo.lock`. | Phase 0.2 |
| **[#297](https://github.com/OpenGamingCollective/asusctl/pull/297)** | `refactor(asusd)` | `refactor/event-driven-sys-events` | ✅ **MERGED** | **Integrated Upstream (`f1691584`)**: Event-driven `logind-zbus` & power monitoring. | Phase 1.1 |
| **[#294](https://github.com/OpenGamingCollective/asusctl/pull/294)** | `fix(gpu)` | `fix/gpu-telemetry-overhaul` | ✅ **MERGED** | **Integrated Upstream (`731d772c`)**: Passive zero-wakeup dGPU telemetry & udev scan deduplication. | Phase 1.1 |

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
  * Solves a long-standing user request: allows setting "Performance" when plugged into AC and "Quiet" when running on Battery.
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
  * Fixes [Issue #304](https://github.com/OpenGamingCollective/asusctl/issues/304). Prevents `.unwrap()` crashes when configuration files are accessed with read-only permissions or in restricted container environments.
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

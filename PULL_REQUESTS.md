# 🔀 Pull Request Catalog & Architectural Assessment

> *Last automated synchronization: 2026-08-18 15:50 UTC*

This document provides an automated audit of upstream pull requests (Open, Merged, and Closed-without-merge) from [`OpenGamingCollective/asusctl`](https://github.com/OpenGamingCollective/asusctl/pulls).

Each pull request is evaluated for its architectural impact, alignment with the **"Async Control, Sync Data"** paradigm, dependency health, and whether it should be merged, kept, or reopened.

---

## 📑 Summary Matrix

| PR # | Type / Area | Branch / Scope | Status | Recommended Action | Roadmap Phase |
| :--- | :--- | :--- | :---: | :--- | :---: |
| **[#317](https://github.com/OpenGamingCollective/asusctl/pull/317)** | `perf(anime): decouple kernel I/O with Co...` | `perf/anime-io-pipeline` | 🔄 **OPEN** | **🟢 KEEP / MERGE: Reference implementation for 'Async Control, Sync Data'** | Phase 1.1 |
| **[#316](https://github.com/OpenGamingCollective/asusctl/pull/316)** | `feat(asusd): remember platform profile p...` | `feat(asusd)/remember-plateform-profile-per-source` | 🔄 **OPEN** | **🟢 KEEP / MERGE: Dynamic AC vs Battery platform profile memory** | Phase 2.5 |
| **[#315](https://github.com/OpenGamingCollective/asusctl/pull/315)** | `rog-control-center: massive refactoring ...` | `clean-and-setup-base` | ✅ **MERGED** | **Merged into rogcc-redesign: Prepares modular pages & accessibility** | Phase 3.4 |
| **[#314](https://github.com/OpenGamingCollective/asusctl/pull/314)** | `refactor: unify image and animation deco...` | `refactor/unify-image-crate` | 🔄 **OPEN** | **🟢 KEEP / MERGE: Consolidated image pipeline under image = '=0.25.9'** | Phase 3.2 |
| **[#312](https://github.com/OpenGamingCollective/asusctl/pull/312)** | `fix(rog-control-center): re-arm global s...` | `fix/global-shortcuts-multi-backend` | 🔄 **OPEN** | **🟢 KEEP / MERGE: Re-arms XDG Global Shortcuts portal upon desktop resume** | Phase 3.3 |
| **[#311](https://github.com/OpenGamingCollective/asusctl/pull/311)** | `chore(asusctl): remove obsolete examples...` | `chore/remove-asusctl-examples` | ⏹️ **CLOSED** | **🟠 REOPEN / MERGE: Purges legacy examples and unneeded check/test targets** | Phase 3.4 |
| **[#310](https://github.com/OpenGamingCollective/asusctl/pull/310)** | `refactor: remove obsolete asusd-user cra...` | `refactor/remove-asusd-user` | ⏹️ **CLOSED** | **🟠 REOPEN / MERGE: Purges obsolete asusd-user crate, units, and packaging bloat** | Phase 1.4 |
| **[#309](https://github.com/OpenGamingCollective/asusctl/pull/309)** | `chore: bump to edition 2024...` | `chore-edition-2024` | ✅ **MERGED** | **Integrated Upstream (6b6cdc63): Migrated workspace to Rust Edition 2024** | Phase 0.2 |
| **[#308](https://github.com/OpenGamingCollective/asusctl/pull/308)** | `chore: bump rust to 1.85.0...` | `chore-bump-rust-to-1.85.0` | ✅ **MERGED** | **Integrated Upstream (84645b6a): Upgraded MSRV to Rust 1.85.0** | Phase 0.2 |
| **[#307](https://github.com/OpenGamingCollective/asusctl/pull/307)** | `Add Aura support for ROG Strix G16 G614P...` | `main` | ✅ **MERGED** | **Integrated Upstream (a1322ff9): Added Aura support for ROG Strix G16 G614PP** | Phase 2.4 |
| **[#306](https://github.com/OpenGamingCollective/asusctl/pull/306)** | `fix(rog-control-center): prevent startup...` | `fix/rog-control-center-startup` | ✅ **MERGED** | **Integrated Upstream (31635a6f): Eliminated nested Tokio runtime startup panics** | Phase 1.1 |
| **[#305](https://github.com/OpenGamingCollective/asusctl/pull/305)** | `fix(config-traits): open read-only confi...` | `fix-readonly-config-open` | 🔄 **OPEN** | **🟢 KEEP / MERGE: Prevents panics on read-only configs (Invariant #5)** | Phase 3.4 |
| **[#303](https://github.com/OpenGamingCollective/asusctl/pull/303)** | `docs: update docs, include new guides, a...` | `docs/re-organize` | ✅ **MERGED** | **Integrated Upstream (5307fd13): Major documentation overhaul & CLI guide** | Phase 4 |
| **[#301](https://github.com/OpenGamingCollective/asusctl/pull/301)** | `refactor(asusd): simplify armoury attrib...` | `refactor/armoury-attribute-persistence` | 🔄 **OPEN** | **🟢 KEEP / MERGE: Simplifies Armoury attribute persistence & boot restoration** | Phase 2.3 |
| **[#300](https://github.com/OpenGamingCollective/asusctl/pull/300)** | `fix(asusd): prevent storing and applying...` | `fix/armoury-unapplicable-tuning-values` | 🔄 **OPEN** | **🟢 KEEP / MERGE: Rejects out-of-bounds Armoury tuning writes to sysfs** | Phase 2.3 |
| **[#298](https://github.com/OpenGamingCollective/asusctl/pull/298)** | `chore: reinstate lockfile...` | `chore/reinstate-lockfile` | ✅ **MERGED** | **Integrated Upstream (dfe4185b): Reinstated committed Cargo.lock** | Phase 0.2 |
| **[#297](https://github.com/OpenGamingCollective/asusctl/pull/297)** | `refactor(asusd): replace polling loops i...` | `refactor/event-driven-sys-events` | ✅ **MERGED** | **Integrated Upstream (f1691584): Event-driven logind-zbus & power monitoring** | Phase 1.1 |
| **[#296](https://github.com/OpenGamingCollective/asusctl/pull/296)** | `feat: add human panic basic functions...` | `feature/human-panic` | ⏹️ **CLOSED** | **🟠 REOPEN / MERGE: User-friendly crash dialogs & sanitized logs across CLI/GUI** | Phase 3.4 |
| **[#294](https://github.com/OpenGamingCollective/asusctl/pull/294)** | `fix(gpu): overhaul GPU telemetry with pa...` | `fix/gpu-passive-agnostic-monitoring` | ✅ **MERGED** | **Integrated Upstream (731d772c): Passive zero-wakeup dGPU telemetry & udev scan deduplication** | Phase 1.1 |
| **[#292](https://github.com/OpenGamingCollective/asusctl/pull/292)** | `feat(rog-slash): add slash support for G...` | `feat/slash-support-gu405` | ✅ **MERGED** | **Integrated Upstream** | Phase 2 / 3 |
| **[#291](https://github.com/OpenGamingCollective/asusctl/pull/291)** | `docs: migrate the asus-linux website con...` | `docs/actual-docs` | ✅ **MERGED** | **Integrated Upstream** | Phase 2 / 3 |
| **[#285](https://github.com/OpenGamingCollective/asusctl/pull/285)** | `Fix Aura interface selection and effect ...` | `main` | ✅ **MERGED** | **Integrated Upstream** | Phase 2 / 3 |
| **[#283](https://github.com/OpenGamingCollective/asusctl/pull/283)** | `docs: init mdbook...` | `docs/mdbook` | ✅ **MERGED** | **Integrated Upstream** | Phase 2 / 3 |
| **[#281](https://github.com/OpenGamingCollective/asusctl/pull/281)** | `feat: add support for ROG Zephyrus G16 G...` | `feat/gu606ax-support` | ✅ **MERGED** | **Integrated Upstream** | Phase 2 / 3 |
| **[#280](https://github.com/OpenGamingCollective/asusctl/pull/280)** | `fix: platform profile handling when quie...` | `fix/platform-profile-cycle-and-epp` | 🔄 **OPEN** | **🟢 KEEP / MERGE: Graceful fallback when firmware lacks Quiet/Low-Power profile** | Phase 2.5 |
| **[#279](https://github.com/OpenGamingCollective/asusctl/pull/279)** | `fix(rog-control-center): app window defa...` | `main` | ✅ **MERGED** | **Integrated Upstream** | Phase 2 / 3 |
| **[#276](https://github.com/OpenGamingCollective/asusctl/pull/276)** | `Remove dead code...` | `remove-dead-code` | ✅ **MERGED** | **Integrated Upstream** | Phase 2 / 3 |
| **[#275](https://github.com/OpenGamingCollective/asusctl/pull/275)** | `[UI redesign 1/3-new] feat(rog-platform)...` | `rogcc-gpu-freq-mhz` | ✅ **MERGED** | **Integrated Upstream** | Phase 2 / 3 |
| **[#273](https://github.com/OpenGamingCollective/asusctl/pull/273)** | `fix(asusd): carry Slash display mode as ...` | `rogcc-slash-u8` | ✅ **MERGED** | **Integrated Upstream** | Phase 2 / 3 |
| **[#272](https://github.com/OpenGamingCollective/asusctl/pull/272)** | `docs(readme): restructure and correct co...` | `patch-1` | ✅ **MERGED** | **Integrated Upstream** | Phase 2 / 3 |
| **[#271](https://github.com/OpenGamingCollective/asusctl/pull/271)** | `Add Aura support for ROG Strix G16 G614P...` | `add-g614pm-aura-support` | ✅ **MERGED** | **Integrated Upstream** | Phase 2 / 3 |
| **[#270](https://github.com/OpenGamingCollective/asusctl/pull/270)** | `fix(asusctl): dynamically resolve D-Bus ...` | `fix/slash-dbus-path` | ✅ **MERGED** | **Integrated Upstream** | Phase 2 / 3 |
| **[#268](https://github.com/OpenGamingCollective/asusctl/pull/268)** | `feat: add GU502GV aura support...` | `main` | ✅ **MERGED** | **Integrated Upstream** | Phase 2 / 3 |
| **[#265](https://github.com/OpenGamingCollective/asusctl/pull/265)** | `build(rog-control-center): compile .mo c...` | `build/compile-install-translations` | ✅ **MERGED** | **Integrated Upstream** | Phase 2 / 3 |
| **[#261](https://github.com/OpenGamingCollective/asusctl/pull/261)** | `fix(asusd): log unsupported armoury attr...` | `fix/armoury-log-once` | ✅ **MERGED** | **Integrated Upstream** | Phase 2 / 3 |
| **[#257](https://github.com/OpenGamingCollective/asusctl/pull/257)** | `asusd: open scsi_generic /dev/sgN for SC...` | `arion-scsi-sg-node` | ✅ **MERGED** | **Integrated Upstream** | Phase 2 / 3 |
| **[#256](https://github.com/OpenGamingCollective/asusctl/pull/256)** | `Add tuning enable/disable and PPT relate...` | `fix/asusctl-ppt-fixes` | ✅ **MERGED** | **Integrated Upstream** | Phase 2 / 3 |
| **[#251](https://github.com/OpenGamingCollective/asusctl/pull/251)** | `refactor: modernize std patterns and cle...` | `refactor/bump-msrv-1.85` | ✅ **MERGED** | **Integrated Upstream** | Phase 2 / 3 |
| **[#249](https://github.com/OpenGamingCollective/asusctl/pull/249)** | `refactor: remove mocking module and asso...` | `cleanup/remove-dead-mocking-code` | ✅ **MERGED** | **Integrated Upstream** | Phase 2 / 3 |
| **[#248](https://github.com/OpenGamingCollective/asusctl/pull/248)** | `fix(rog-control-center): resolve legacy ...` | `fix/mocking-all-features` | ✅ **MERGED** | **Integrated Upstream** | Phase 2 / 3 |
| **[#241](https://github.com/OpenGamingCollective/asusctl/pull/241)** | `refactor: Remove rust-cache from release...` | `rustup` | ✅ **MERGED** | **Integrated Upstream** | Phase 2 / 3 |
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

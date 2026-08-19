# Major Refactoring & Architecture Modernization Specification for `asusctl`

This document details the comprehensive architectural refactoring, optimization, and modernization plan for the `asusctl` codebase (`asusd`, `asusctl`, `rog-control-center`, and associated sub-crates).

The primary goal of this initiative is **code simplification**, **elimination of async concurrency deadlocks**, **protocol safety**, **crate optimization**, and a **progressive transition toward kernel driver delegation**, establishing a robust, testable, and lightweight user-space policy orchestrator.

> **Commit Baseline**: Verified against `OpenGamingCollective/asusctl` at commit `dfe4185b` / `d46a24ce` (Release `6.4.0+`).  
> **Target MSRV & Edition**: **Rust 1.85** with **Rust Edition 2024** (✅ Integrated upstream in commits `84645b6a` and `6b6cdc63`; establishes `[workspace.package]` inheritance, `unsafe_op_in_unsafe_fn` enforcement, and unlocks modern ecosystem dependencies).

---

## 🎯 Executive Summary & Upstream Status

Historically, `asusctl` accumulated custom user-space driver routines (raw WMI calls, raw HID packet crafting, custom powercap limit parsing) and nested concurrency locks (`Arc<Mutex<...>>`) to work around older Linux kernel limitations.

Recent upstream releases (v6.4.0+) have already resolved several initial pain points:
* ✅ **Rust 1.85 & Edition 2024 Workspace Migration**: Upgraded `rust-version = "1.85"` and `edition = "2024"` across all workspace crates (`84645b6a`, `6b6cdc63`), updated `clippy.toml` (`dfe4185b`), handled `unsafe_op_in_unsafe_fn` explicit blocks, pinned 1.85-compatible dependencies (`fontdue = "=0.9.3"`, `slint = "=1.13.1"`, `zbus = "=5.13.2"`), and replaced unsafe `env::set_var` with `env_logger::Builder::from_env`.
* 🔄 **AniMe Matrix Image & Decoding Unification ([PR #314](https://github.com/OpenGamingCollective/asusctl/pull/314))**: Unifies all image and animation decoders workspace-wide under `image = "=0.25.9"`, purging legacy direct dependencies (`png_pong`, `pix`, `gif`, `png`), resolving multi-frame GIF/APNG subframe offset regressions, and streamlining canvas conversions.
* 🔄 **AniMe Matrix Kernel I/O Decoupling & Zero-Copy Proxy ([PR #317](https://github.com/OpenGamingCollective/asusctl/pull/317))**: Decoupled blocking USB HID kernel I/O from the Tokio async executor using a dedicated background worker thread with a `Condvar` mailbox and FIFO control queue. Introduces zero-copy `&AnimeDataBuffer` D-Bus proxy methods (`rog-dbus`, `rog-anime`) and frame pre-computation to eliminate D-Bus timeouts and UI stuttering.
* ✅ **`thiserror v2` Workspace Standardization**: All workspace crates have been upgraded to `thiserror = "^2.0.19"`.
* ✅ **Event-Driven Power/Lid Monitoring**: Polling loops in `create_sys_event_tasks` were replaced with event-driven `logind-zbus` and a shared udev monitor (`f1691584`).
* ✅ **Elimination of UI Runtime Panics**: Removed nested Tokio runtime crashes in `rog-control-center` (`31635a6f`).
* ✅ **GPU Telemetry Streamlining**: Eliminated `lspci` process spawning, deduplicated udev scans, shared NVML handles, and added runtime power management awareness to avoid waking suspended dGPUs.

The remaining roadmap adopts a **pragmatic two-track strategy**:

1. **Immediate User-Space Refactoring & Optimization**: Modernize daemon internals — eliminate remaining nested `Arc<Mutex<...>>` locks via Tokio actors to fix D-Bus deadlocks, replace the legacy `mio` thread and nested Tokio runtimes in `aura_manager.rs` and `start_power_monitor` with a dedicated synchronous udev worker thread and asynchronous mailbox (`mpsc::channel`), purging the `mio` dependency without adding external stream crates, decouple code into a clean 3-layer architecture, migrate tooling to native Cargo workspace lints (`[workspace.lints]`), and introduce `sysfs` provider traits for non-root CI testing.
2. **Progressive Kernel Offloading**: Opportunistically delegate low-level hardware driving to Linux kernel modules (`asus-wmi`, `asus-armoury`, `hid-asus`, `/sys/class/firmware_attributes/`) as modern kernel versions (7.0+) become widespread, keeping user-space fallback adapters modular.

> 📚 **Dedicated Upstream Companion Catalogs**:
> * **[🔀 Pull Request Catalog & Audit (`PULL_REQUESTS.md`)](PULL_REQUESTS.md)**: Full audit of all open, merged, and closed pull requests, architectural impact assessments, and reopening recommendations.
> * **[🐛 Upstream Issues Audit & Roadmap Mapping (`ISSUES.md`)](ISSUES.md)**: Deep classification of all active issues (hardware quirks, zero-wakeup dGPU telemetry, D-Bus leaks, panics) mapped to roadmap solutions.

---

## 🔒 Mandatory Governance & Engineering Invariants

All refactoring tasks and PRs must strictly comply with the following invariants:

1. **Rust 1.85 MSRV & Edition 2024 Baseline**: Workspace MSRV is strictly **Rust 1.85** with **Rust Edition 2024** (now merged upstream). All new code and refactorings must comply with Edition 2024 semantics (e.g. `unsafe_op_in_unsafe_fn` by default, RPITIT precise capturing `use<..>`, native `[workspace.package]` inheritance) and avoid unpinned dependencies requiring rustc > 1.85.
2. **"Async Control, Sync Data" Architectural Paradigm**: Strictly decouple the asynchronous control plane from synchronous hardware execution. Never execute blocking hardware I/O inside Tokio tasks, and never simulate synchronous polling inside async contexts (e.g. busy loops checking `AtomicBool` or sleeping). Use Tokio strictly for passive event multiplexing (D-Bus, timers, udev events) and offload uninterruptible kernel/USB I/O to dedicated OS worker threads with Condvar/channel mailboxes.
3. **Measurement-Driven Execution**: No performance claim is valid without before/after benchmarks. Optimization priority belongs strictly to clean/incremental build times, binary size (`.text` section), RSS memory, timer wakeups (`powertop`), and protocol correctness.
4. **LOC is an Observation, Not a KPI**: Source LOC reduction is recorded for maintainability reporting only. No task may be approved or rejected based on LOC delta alone.
5. **Zero `.unwrap()` Prohibition**: Never use `.unwrap()` in production code. Use proper error propagation (`?`), pattern matching, or `.expect("Clear explanation of invariant")`.
6. **Strict `unsafe` Control**: Avoid `unsafe` blocks whenever safe Rust abstractions exist. Any mandatory `unsafe` block MUST be preceded by a mandatory `// SAFETY:` doc comment explaining memory safety invariants (enforced by Edition 2024's default `unsafe_op_in_unsafe_fn` rules).
7. **D-Bus Backward Compatibility**: Preserve existing D-Bus method signatures and object paths (`/org/asuslinux/...`) so external clients (`rog-control-center`, GNOME extensions) continue functioning seamlessly.
8. **Native Cargo Workspace Lints**: External lint tools (`Cranky.toml`) are retired in favor of native `[workspace.lints]` in root `Cargo.toml`.

---

## 🗺️ Implementation Roadmap

```text
┌──────────────────────────────────────────────────────────────────────────┐
│ Phase 0: Baseline Benchmark Harness & Environment Setup                  │
├──────────────────────────────────────────────────────────────────────────┤
│  ├── 0.1 Reproducible Profiling Protocol (Build time, .text size, RSS)   │
│  └── 0.2 Workspace MSRV 1.85 & Edition 2024 Baseline (✅ UPSTREAM)       │
└───────────────────────────────────┬──────────────────────────────────────┘
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────────────────────┐
│ Phase 1: Immediate User-Space Concurrency & Tooling Modernization        │
├──────────────────────────────────────────────────────────────────────────┤
│  ├── 1.1 State Architecture: Actor Model (Lock Elimination)              │
│  ├── 1.2 Tooling Modernization: Cranky.toml -> Native [workspace.lints]  │
│  └── 1.3 Git Hook Infrastructure: cargo-husky -> Native .githooks        │
└───────────────────────────────────┬──────────────────────────────────────┘
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────────────────────┐
│ Phase 2: Architectural Decoupling & Gradual Kernel Offloading            │
├──────────────────────────────────────────────────────────────────────────┤
│  ├── 2.1 Driver vs Daemon Decoupling (3-Layer Architecture)              │
│  ├── 2.2 Progressive Kernel Offloading & Driver Delegation               │
│  ├── 2.3 Armoury Attribute Management (Pub/Sub Event System)             │
│  └── 2.4 Device Identity & Quirks Engine (`dmi-id` Modernization)        │
└───────────────────────────────────┬──────────────────────────────────────┘
                                    │
                                    ▼
┌───────────────────────────────────────────────────────────────────────────┐
│ Phase 3: Protocol Safety, Ergonomics, Event Loop & CLI                    │
├───────────────────────────────────────────────────────────────────────────┤
│  ├── 3.1 USB HID Wire Protocol Safety (`zerocopy`)                        │
│  ├── 3.2 PNG & Raster Pipeline Modernization (`rog-anime` image migration)│
│  ├── 3.3 Hardware Event Stream & Mailbox (`aura_manager.rs` -> Udev Worker) │
│  └── 3.4 Ergonomic Types & CLI Modernization (`clap` v4, `strum`, flags)  │
└───────────────────────────────────┬───────────────────────────────────────┘
                                    │
                                    ▼
┌───────────────────────────────────────────────────────────────────────────┐
│ Phase 4: Testability, Observability & Automation                          │
├───────────────────────────────────────────────────────────────────────────┤
│  ├── 4.1 `sysfs` Abstraction & Hardware Mocking (`SysfsProvider`)         │
│  ├── 4.2 Asynchronous Observability & Structured Tracing (`tracing`)      │
│  └── 4.3 Automated Integration Testing Suite (`uhid-virt` & E2E)          │
└───────────────────────────────────────────────────────────────────────────┘
```

---

## Phase 0: Baseline Benchmark Harness & Setup

### 0.1 Reproducible Profiling Protocol
Before undertaking major refactorings, empirical baseline metrics must be recorded into `baseline.json`:
* **Build Time**: Clean release build (median of 3 runs) and incremental release build (median of 5 runs).
* **Binary Footprint**: Executable size, `.text` section size, and `cargo bloat` output for `default-members` (`asusd`, `asusctl`, `asusd-user`, `asus-shutdown`, `rog-control-center`).
* **Runtime Overhead**: Idle RSS memory, thread count, CPU usage, open file descriptors, and timer wakeups/sec (`powertop`).

### 0.2 Workspace MSRV 1.85 & Edition 2024 Baseline (✅ Completed Upstream)
* **Upstream Integration (`84645b6a`, `6b6cdc63`, `dfe4185b`)**:
  * Set `rust-version = "1.85"` and `edition = "2024"` in `[workspace.package]` in root `Cargo.toml`.
  * Migrated all workspace member crates to **Rust Edition 2024**, standardizing configuration via `edition.workspace = true` and `rust-version.workspace = true`.
  * Handled Edition 2024 compiler requirements:
    * **`unsafe_op_in_unsafe_fn`**: Explicit `unsafe` blocks placed inside `unsafe fn`, pairing with our mandatory `// SAFETY:` doc comment invariant.
    * **Safe Env Logger**: Replaced `unsafe { env::set_var(...) }` calls with `env_logger::Builder::from_env(...)`.
    * **Matching Patterns**: Fixed irrefutable `if let` pattern warnings.
    * **MSRV 1.85 Dependency Pinning**: Pinned crates requiring newer rustc (e.g. `fontdue = "=0.9.3"` for `u*::cast_signed`, `slint = "=1.13.1"`, `zbus = "=5.13.2"`).
    * **Clippy Configuration**: Configured `clippy.toml` with `msrv = "1.85"`.
* **Refactoring Implications**: All subsequent refactoring phases build directly on this stable Edition 2024 baseline.

---

## Phase 1: Immediate User-Space Concurrency & Tooling Modernization

### 1.1 State Architecture: Actor Model & Universal "Async Control, Sync Data" Mailbox Decoupling

* **Current Issue**: The daemon still relies on nested asynchronous concurrent locks (`Arc<Mutex<AuraConfig>>`, `Arc<Mutex<HidRaw>>`, `Arc<Mutex<HashMap<...>>>`). In `aura_manager.rs`, structures like `Arc<Mutex<HashMap<String, Arc<Mutex<HidRaw>>>>>` cause D-Bus calls to deadlock asynchronously at startup or reload. Furthermore, synchronous USB/HID and sysfs kernel I/O performed directly inside async task loops blocks the Tokio reactor and creates latency jitter on D-Bus.
* **Refactoring Proposal**:
  * Implement the **"Async Control, Sync Data" Mailbox & Worker Pattern** universally across **all daemon hardware controllers**:
    * **1. AniMe Matrix (`asusd::aura_anime`, `rog-anime`)**: Prototyped and validated in [PR #317](https://github.com/OpenGamingCollective/asusctl/pull/317). Tokio handles frame scheduling and zero-copy D-Bus buffering (`&AnimeDataBuffer`); a dedicated worker thread with an `Arc<Condvar>` single-slot mailbox executes blocking USB HID transfers.
    * **2. Aura Keyboard & LED Zones (`asusd::aura_laptop`, `rog-aura`, `asusd::aura_manager`)**:
      * Replaces nested `Arc<Mutex<HashMap<String, Arc<Mutex<HidRaw>>>>>` and inline `hid.lock().await.write(...)` calls.
      * A dedicated sync HID worker thread exclusively owns the `/dev/hidraw` handle and listens to a single-slot mailbox (`Arc<(Mutex<Option<LedMatrix>>, Condvar)>`).
      * Tokio animation tasks (Rainbow, Breathe, Pulse, Comet) calculate matrix states and deposit pre-computed frames into the mailbox without holding lock contention over D-Bus setter calls.
    * **3. Slash Lighting (`asusd::aura_slash`, `rog-slash`)**:
      * Replaces `hid: Option<Arc<Mutex<HidRaw>>>` and `usb: Option<Arc<Mutex<USBRaw>>>`.
      * A dedicated Slash Mailbox worker thread consumes brightness commands and animation packet buffers, completely decoupling USB transfer latency from D-Bus methods.
    * **4. ROG Ally Backlight & SCSI (`asusd::aura_scsi`, `rog-scsi`)**:
      * Replaces `device: Arc<Mutex<Device>>` and blocking raw SCSI command writes (`/dev/sg*`) inside async D-Bus handlers.
      * Dedicated SCSI Mailbox worker thread consumes a FIFO command queue and issues uninterruptible SCSI payload blocks off the Tokio reactor.
    * **5. Armoury BIOS Attributes & Tuning (`asusd::asus_armoury`, `rog-platform`)**:
      * Replaces synchronous sysfs file writes (`/sys/class/firmware_attributes/asus-armoury/attributes/`) performed directly within async D-Bus setter handlers.
      * A dedicated sysfs writer thread consumes a serialized mailbox channel (`tokio::sync::mpsc::channel<(Attribute, AttrValue)>`), guaranteeing that ACPI/kernel sysfs delays never stall D-Bus dispatchers.
    * **6. Fan Curves & Platform Profiles (`asusd::ctrl_fancurves`, `asusd::ctrl_platform`)**:
      * Replaces cross-referencing `Arc<Mutex<Config>>` and `Arc<Mutex<FanCurveConfig>>` locks.
      * Synchronized profile dispatch mailbox receives thermal policy transitions and applies PWM curve tables and PPT power limits sequentially.
    * **7. Hardware Udev Hotplug Monitoring (`asusd::aura_manager`, `start_power_monitor`)**:
      * Dedicated sync OS thread listens on the kernel netlink udev socket and feeds a `tokio::sync::mpsc` mailbox, eliminating `mio` polling loops and nested `Runtime::new()` instances.
    * **8. Client Tools & UI (`rog-control-center`, `asusctl`)**:
      * Pure async IPC clients interacting via non-blocking D-Bus proxies (`zbus`) and `tokio::sync::watch` telemetry channels, with zero internal blocking threads or UI freezes.
* **Target Benefits**:
  * Total elimination of concurrency lock contention and D-Bus deadlocks across all hardware features.
  * Clean, deterministic execution flow: zero hardware bus latency leaks into Tokio executor threads.
  * 100% testable via mock mailbox receivers and virtual hardware channels without physical hardware.

### 1.2 Tooling Modernization: `Cranky.toml` → Native `[workspace.lints]`

* **Current Issue**: The repository uses an external wrapper configuration (`Cranky.toml`, 118 lines, 107 clippy error overrides) rather than standard Cargo workspace lint inheritance.
* **Refactoring Proposal**: Migrate all clippy, rustc, and rustdoc policy rules directly into `[workspace.lints.clippy]`, `[workspace.lints.rust]`, and `[workspace.lints.rustdoc]` in root `Cargo.toml`. Member crates inherit policy via `[lints] workspace = true` alongside `[package] edition.workspace = true`.
* **Target Benefits**: Zero reliance on external binary wrappers; standard `cargo clippy` and `cargo check` enforce workspace-wide lint compliance.

### 1.3 Git Hook Infrastructure: `cargo-husky` → Native `.githooks`

* **Current Issue**: `cargo-husky` adds build-script overhead to dev dependencies for copying git hooks on build.
* **Refactoring Proposal**: Replace `cargo-husky` with native git hooks stored in `.githooks/` and configured via `git config core.hooksPath .githooks`. Ensure CI execution is completely independent of local developer git hooks.

### 1.4 Crate Consolidation: Deprecate & Purge `asusd-user` ([PR #310](https://github.com/OpenGamingCollective/asusctl/pull/310))

* **Current Status & Rationale**:
  * `asusd-user` was originally created as a per-user session daemon.
  * In current architecture, `asusd` exposes all features (Aura, AniMe, Armoury, fan curves) directly on the system D-Bus (`/org/asuslinux/...`), and all tooling (`asusctl`, `rog-control-center`, GNOME extensions) connects exclusively to `asusd`.
  * Maintaining `asusd-user` causes dual-daemon packaging confusion, duplicate systemd services, and workspace compile overhead.
* **Refactoring Proposal**:
  * Reopen and integrate [PR #310](https://github.com/OpenGamingCollective/asusctl/pull/310): delete `asusd-user/` crate, `asusd-user.service`, and update distribution packaging scripts (`PKGBUILD`, `Makefile`) with upgrade cleanup hooks (`cleanup_asusd_leftovers`).
* **Target Benefits**:
  * Eliminates crate bloat and packaging confusion across distros; reduces total workspace build times.

---

## Phase 2: Architectural Decoupling & Gradual Kernel Offloading

### 2.1 Driver vs Daemon Decoupling (3-Layer Architecture)

* **Current Issue**: Low-level hardware driving logic is tightly coupled within `asusd` alongside D-Bus service logic and configuration serialization formats.
* **Refactoring Proposal**: Structurally split the codebase into three distinct layers:
  1. **Adaptor Layer (Driver/Kernel)**: Standalone modules interfacing with kernel sysfs/WMI interfaces or fallback USB/HID communication.
  2. **Core Engine (Policy & State)**: The actual daemon, which decides behavioral policies, applies user preferences, and responds to system state changes (power supply, suspend, throttling profiles).
  3. **IPC Layer (D-Bus Interfaces)**: A thin layer exposing D-Bus interfaces via `zbus` and translating remote calls into channel messages for the Core Engine.

### 2.2 Progressive Kernel Offloading & Driver Delegation

* **Current Issue**: Custom user-space WMI/HID driver routines require ongoing maintenance for each new laptop generation. Upstreaming native kernel drivers takes time, requiring a phased transition.
* **Refactoring Proposal**:
  * Detect available kernel interfaces (`asus-armoury`, `asus-wmi`, `/sys/class/firmware_attributes/`) at boot via `GetSupported`.
  * Offload hardware operations (e.g. power limits, fan curves, BIOS attributes) to native kernel nodes when present.
  * Maintain clean, isolated user-space fallback adapters in the Adaptor Layer for older kernels.
* **Target Benefits**:
  * Progressive code cleanup without breaking hardware compatibility on older kernels.
  * Seamless transition to kernel-native interfaces as users update their kernels.

### 2.3 Armoury Attribute Validation, Schema & Persistence ([PR #300](https://github.com/OpenGamingCollective/asusctl/pull/300), [PR #301](https://github.com/OpenGamingCollective/asusctl/pull/301))

* **Current Issue**: Direct writes to `/sys/class/firmware_attributes/asus-armoury/attributes/` lack input bounds checking and error self-healing, risking corrupt JSON state in `/var/lib/asusd/armoury.json` and boot failure loops on unapplicable attributes.
* **Refactoring Proposal**:
  * Merge [PR #300](https://github.com/OpenGamingCollective/asusctl/pull/300) to reject invalid attribute values before writing to sysfs.
  * Merge [PR #301](https://github.com/OpenGamingCollective/asusctl/pull/301) to simplify Armoury attribute JSON serialization and self-healing state restoration.
  * Implement Publisher-Subscriber event synchronization: updating an attribute emits an asynchronous `AttributeChanged` event, allowing decoupled handlers (e.g. `IntelPowerSync`) to respond without polluting core attribute logic.

### 2.4 Device Identification, DMI Taxonomy & Hardware Quirks Engine (`dmi-id` Modernization)

* **Current Issue**: `dmi-id` is an isolated micro-crate (~80 LOC) that only performs flat string extraction via `udev`. ASUS model classification and quirk detection are fragmented and duplicated across 6 crates (`asusd`, `asusctl`, `rog-control-center`, `rog-anime`, `rog-slash`, `rog-aura`) using fragile `board_name.contains(...)` string matching. Furthermore, DMI reading lacks a direct `/sys/class/dmi/id/` filesystem fallback and cannot be mocked without unsafe environment variable hacks, causing tests to be ignored in CI (`#[ignore]`).
* **Refactoring Proposal**:
  * **Strongly-Typed ASUS Taxonomy**: Centralize model and family parsing into rich domain types (`DeviceFamily`, `ModelYear`, `AnimeType`, `SlashType`).
  * **Unified Query APIs**: Expose high-level feature checks (`is_rog_ally()`, `is_tuf()`, `supported_keyboard_backend()`, `fan_count()`) eliminating duplicate substring matches.
  * **Resilient Dual-Layer DMI Reader**: Implement direct `/sys/class/dmi/id/` reading with udev enrichment for container and non-udev environments.
  * **100% Mockable Test Harness**: Support `DMIID::from_sysfs_path` and `DMIID::mock(...)` integrating seamlessly with `SysfsProvider` (Section 4.1) and `simulators` for non-ASUS CI testing.
  * **Workspace Consolidation**: Integrate into `rog-platform` (or modernize as a full-featured identity engine) to eliminate micro-crate overhead.
* **Target Benefits**:
  * Eliminates model parsing duplication and fragile string matching across the workspace.
  * Enables offline unit and integration testing of model-specific behavior in CI.
  * Sits cleanly between driver detection and daemon policy dispatch.

### 2.5 Power Policy & Platform Profile per Power Source ([PR #316](https://github.com/OpenGamingCollective/asusctl/pull/316), [PR #280](https://github.com/OpenGamingCollective/asusctl/pull/280))

* **Refactoring Proposal**:
  * **Dynamic AC/Battery Profile Switching ([PR #316](https://github.com/OpenGamingCollective/asusctl/pull/316))**: Track and restore preferred platform profiles independently for AC and Battery power sources, seamlessly transitioning via `logind` power supply events.
  * **Missing ACPI Profile Graceful Fallback ([PR #280](https://github.com/OpenGamingCollective/asusctl/pull/280))**: Prevent daemon startup failures on models where firmware omits the `Quiet` or `Low-Power` profile.

---

## Phase 3: Protocol Safety, Ergonomics, Event Loop & CLI

### 3.1 USB HID Wire Protocol Safety (`zerocopy`)

* **Current Issue**: `rog-anime` and `rog-aura` construct 640-byte USB HID packets (`pub type AnimePacketType = Vec<[u8; 640]>`) using manual byte slicing and index offset calculations.
* **Refactoring Proposal**: Use `zerocopy` to define strongly-typed HID packet header and payload structures using `#[repr(C)]` with explicit endian types (`U16<LittleEndian>`, `U32<LittleEndian>`) and `Unaligned`.
* **Target Benefits**:
  * Eliminates out-of-bounds slicing crashes.
  * Zero-cost serialization/deserialization validated against byte-for-byte golden wire tests.

### 3.2 PNG & Raster Pipeline Modernization (`rog-anime` & Workspace Image Consolidation)

* **Current Status & Reference PR ([PR #314](https://github.com/OpenGamingCollective/asusctl/pull/314))**:
  * Replaced `png_pong` and `pix` simultaneously with `image` (`=0.25.9`), mapping decoders directly from PNG/APNG to `Vec<Pixel>` for `AnimeImage`.
  * Replaced the standalone `gif` crate with `image::codecs::gif::GifDecoder`.
  * Purged `png_pong`, `pix`, `gif`, and standalone `png` from workspace dependencies.
  * Fixed canvas coordinate conversions and subframe offset rendering regressions for animated GIFs and APNGs.
* **Target Benefits**:
  * Consolidates all raster image decoding across the workspace into a single robust dependency (`image`).
  * Eliminates 4 redundant image crates (`png_pong`, `pix`, `gif`, `png`).
  * Verified against golden pixel oracle tests for color luminance, alpha blending, and APNG frame compositing.

### 3.3 Hardware Event Stream & Task Lifecycle Modernization (Udev Sync Worker + Mailbox Channel & `mio` Purge)

* **Current Issue**:
  * In `aura_manager.rs:L583-612`, a dedicated OS thread runs a `mio` polling loop on udev, creates an **entire nested Tokio runtime** (`Runtime::new()`), and calls `rt.block_on(...)` inside the loop for dynamic D-Bus device additions/removals.
  * In `asusd/src/lib.rs:L134-210` (`start_power_monitor`), a separate dedicated OS thread is spawned purely to poll `mio` for power supply changes (AC/Battery) and bridge events to a `watch::channel`.
  * The workspace pulls `mio = "^1.2.2"` and `udev = { ..., features = ["mio"] }` solely for these two manual polling loops.
  * Several background loops across the workspace simulate synchronous behavior within async tasks via `AtomicBool` flags (`while running.load(...) { tokio::time::sleep(...) }`) or perform blocking syscalls directly on the async executor.
* **Refactoring Proposal**:
  * **Udev Sync Worker Thread with Tokio Mailbox Channel (`tokio::sync::mpsc`)**:
    * Spawn a lightweight, dedicated synchronous OS thread that listens directly to the kernel's netlink udev socket (`udev::MonitorBuilder::new()?.listen()?`) via blocking syscalls.
    * **Zero Idle CPU Overhead**: The thread sleeps passively inside kernel netlink `recv`/`poll` with zero timer wakeups and wakes up strictly when the kernel emits a physical hardware event (`add`, `remove`, `change`).
    * **Mailbox Event Dispatch**: When a device event occurs (e.g. Aura USB device plugged/unplugged, SCSI device node change, power supply transition), the worker parses the event into a strongly-typed `DeviceHotplugEvent` enum and sends it over a bounded asynchronous channel (`tokio::sync::mpsc::Sender<DeviceHotplugEvent>`).
    * **Zero Additional External Crates**: Avoids introducing `tokio-udev` or complex `AsyncFd` polling logic, perfectly embodying the *"Async Control, Sync Data"* paradigm (synchronous kernel socket listening on an OS worker, asynchronous actor state management on Tokio).
    * **Purge `mio` Dependency**: Completely remove `mio = "^1.2.2"` and `udev`'s `mio` feature flag from workspace dependencies.
    * **Eliminate Nested Runtimes**: Eradicate secondary `tokio::runtime::Runtime` instantiations and blocking calls.
  * **Workspace-Wide Elimination of `AtomicBool` Polling**: Replace all manual `AtomicBool` polling loops across `asusd`, `asusd-user`, and `rog-control-center` with `tokio_util::sync::CancellationToken`, `tokio::sync::watch`, and `tokio::select!` for clean, instant, cooperative task cancellation and hot-reload.
  * **Strict Isolation of Blocking I/O**: Guarantee that no task executing on Tokio performs blocking syscalls; all blocking work must be dispatched to sync worker threads or `tokio::task::spawn_blocking` (for one-off FS ops).
* **Target Benefits**:
  * Completely eliminates dedicated blocking `mio` threads, nested runtime instantiations, and the `mio` workspace dependency without adding new third-party async stream crates.
  * Eliminates timer wakeups caused by artificial polling loops, minimizing idle CPU usage and battery drain.
  * Deterministic, zero-overhead task lifecycle management during device hot-unplug and daemon reloads.

### 3.4 Ergonomic Types & CLI Modernization

* **CLI Framework (`asusctl`)**: Migrate from `argh` to `clap` (v4 with derive) for improved subcommands, value validation, interactive table rendering (`tabled`), shell completions (`clap_complete`), and man pages.
* **Safe Configuration Loading ([PR #305](https://github.com/OpenGamingCollective/asusctl/pull/305))**: Ensure config file readers gracefully handle read-only filesystems or unprivileged read permissions without panicking.
* **Crash Reporting Ergonomics ([PR #296](https://github.com/OpenGamingCollective/asusctl/pull/296))**: Integrate `human-panic` across binaries (`asusctl`, `rog-control-center`, `asusd`) to present user-friendly error dialogs and log dumps rather than raw stacktraces.
* **Orphan Example & Target Cleanup ([PR #311](https://github.com/OpenGamingCollective/asusctl/pull/311))**: Purge obsolete standalone examples in `asusctl/examples/` and dev-dependencies to streamline compilation targets.
* **Enum Conversions (`strum`)**: Apply `strum` to purely syntactic string-to-enum conversions (e.g. `AuraModeNum`).
* **Hardware Capability Flags (`bitflags`)**: Replace raw capability integers and boolean flags with strongly-typed `bitflags` structs for keyboard lighting zones and power modes.
* **Procfs Reading (`rog-platform`)**: Replace manual string parsing loops in `/proc/` with `procfs` for reading CPU and thermal information.

---

## Phase 4: Testability, Observability & Automation

### 4.1 `sysfs` Abstraction & Hardware Mocking (`SysfsProvider`)

* **Current Issue**: Direct `std::fs::write` and `read_to_string` calls are scattered across `asusd` and `rog-platform`, preventing unit/integration testing on CI or non-ASUS machines.
* **Refactoring Proposal**: Introduce a `SysfsProvider` trait (`RealSysfs` for daemon runtime, `MockSysfs` for test environments).
* **Target Benefits**:
  * Full test coverage of daemon profile logic and Armoury attribute management without requiring root privileges or physical hardware.
  * Reliable CI test execution.

### 4.2 Asynchronous Observability & Structured Tracing (`tracing` Migration)

* **Current Issue**: `asusd` handles concurrent async events using standard `log` (`env_logger`), making it difficult to trace async task execution flows across channels.
* **Refactoring Proposal**: Phased rollout of `tracing` and `tracing-subscriber`, introducing structured spans for D-Bus requests, device hotplug, and state transitions.
* **Target Benefits**:
  * Instant identification of async deadlocks, request timeouts, and state transition races.
  * Structured log output compatible with `systemd-journald`.

### 4.3 Automated Integration Testing Suite (`uhid-virt` & Simulators)

* **Refactoring Proposal**: Create an E2E integration test runner using `uhid-virt` and virtual D-Bus session buses to test `asusctl` CLI commands against a live daemon instance in CI.

---

## 🛠️ Daemon Architecture & Design Patterns

When refactoring daemon components, the following architectural patterns must be preserved and updated to actor/task abstractions:

### 🏛️ The Target Pattern: "Async Control, Sync Data"

Rather than an arbitrary hybrid, the decoupled model is the **idiomatic Rust systems pattern for hardware control**:

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                      TOKIO ASYNC CONTROL PLANE                              │
│                                                                             │
│   ┌─────────────────┐       ┌────────────────────┐    ┌─────────────────┐   │
│   │  D-Bus (zbus)   │       │ Animation Timers / │    │  System Events  │   │
│   │ System Service  │       │ Frame Schedulers   │    │  (Udev Mailbox Rx)│   │
│   └────────┬────────┘       └─────────┬──────────┘    └────────┬────────┘   │
│            │                          │                        │            │
│            ▼                          ▼                        ▼            │
│       ┌────────────────────────────────────────────────────────────┐        │
│       │        Cooperative Task Multiplexing & Actor Dispatch      │        │
│       │  (tokio::select!, CancellationToken, tokio::sync::watch)   │        │
│       └─────────────────────────────┬──────────────────────────────┘        │
└─────────────────────────────────────┼───────────────────────────────────────┘
                                      │ Single-Slot Mailbox / FIFO Queue
                                      │ (&DataBuffer, Arc<Condvar>, mpsc)
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                   HARDWARE WORKER PLANE (OS THREADS)                        │
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │ Dedicated Sync Worker Thread (std::thread / Mailbox)                │   │
│   │                                                                     │   │
│   │  • Uninterruptible blocking USB HID writes (rusb / hidraw)          │   │
│   │  • Blocking sysfs / WMI kernel file operations                      │
│   │  • Blocking kernel netlink udev socket listener (Mailbox Tx)        │   │
│   │  • Zero latency jitter leaked to Tokio async reactor                │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

1. **Tokio Control Plane (Network & System Coordination)**:
   - **Scope**: D-Bus daemon endpoints (`zbus`), animation frame tick timers (`tokio::time::interval`), configuration file watching, system signals (`logind-zbus`, udev mailbox receiver channel), and client request validation.
   - **Characteristics**: Ultra-lightweight passive event waiting. Handles concurrent client calls without blocking.
2. **Mailbox / OS Thread Worker Plane (Hardware Data I/O)**:
   - **Scope**: Low-level USB HID transfers (`rog-anime`, `rog-aura`), raw SCSI commands (`rog-scsi`), and sysfs kernel attribute writes (`asus-armoury`).
   - **Characteristics**: Receives ready/pre-computed data buffers and executes uninterruptible, blocking kernel/USB calls in dedicated OS threads, keeping hardware bus latency and transfer delays isolated from D-Bus and the async reactor.

### 🧹 Cleaning Up Tokio: Eradicating Synchronous Simulation

Rather than removing the async executor, maximizing Tokio's performance requires eliminating anti-patterns that simulate synchronous behavior in async tasks:

* ❌ **Eliminate `AtomicBool` Polling Loops**: Never run `while atomic_flag.load(...) { tokio::time::sleep(...) }` inside async tasks.
* ✅ **Adopt Event-Driven Synchronization**: Use `tokio_util::sync::CancellationToken`, `tokio::sync::watch`, or `tokio::select!` for cooperative cancellation and immediate state change propagation.
* ❌ **Eliminate Blocking Calls in Async Handlers**: Never execute raw `rusb` writes, `std::thread::sleep`, or synchronous file I/O within async task handlers.
* ✅ **Decouple via Mailboxes & Channels**: Forward commands and buffers to dedicated synchronous worker threads via `Condvar` mailboxes (as implemented in PR #317) or bounded channels.

### Controller Traits

* **`GetSupported`**: Checks hardware/kernel features before controller initialization.
* **`Reloadable`**: Reloads configuration and state dynamically without restarting `asusd`.
* **`CtrlTask`**: Runs background tasks, monitors system signals (suspend/resume/boot), and watches configuration paths.
* **`ZbusAdd`**: Exposes controller interfaces cleanly on the system bus via `zbus`.

### Lock Elimination Guidelines

1. Avoid wrapping controllers in `Arc<Mutex<T>>`.
2. Route external D-Bus invocations and background tasks through Tokio `mpsc` channels or Mailbox workers owning the controller state.
3. If an async lock is strictly required in legacy task loops, use non-blocking `try_lock()` inside task event callbacks to prevent deadlocks when system events fire concurrently.

---

## 📊 Summary Matrix of Workspace Improvements & Modernization

| Improvement / Candidate Crate | Status / Scope | Priority | Target Benefit |
| :--- | :---: | :---: | :--- |
| **`thiserror` v2 Uniformity** | ✅ **INTEGRATED UPSTREAM** | — | `thiserror = "^2.0.19"` standardized across all workspace crates in v6.4.0. |
| **Event-Driven Sys Monitors** | ✅ **INTEGRATED UPSTREAM** | — | Polling loops replaced by `logind-zbus` & udev monitor in `create_sys_event_tasks`. |
| **GPU Telemetry Optimization** | ✅ **INTEGRATED UPSTREAM** | — | Eliminated `lspci` spawning, shared NVML handle, runtime PM awareness. |
| **Rust 1.85 & Edition 2024** | ✅ **INTEGRATED UPSTREAM** | — | Upgraded workspace MSRV to 1.85 & Edition 2024 across all crates (`84645b6a`, `6b6cdc63`, `dfe4185b`). |
| **`[workspace.lints.clippy]`** | 🟢 **APPROVED** | 🔴 **P0** | Native Cargo workspace lint policy replacing `Cranky.toml`. |
| **`cargo-husky` → `.githooks`** | 🟢 **APPROVED** | 🟠 **P1** | Native git hooks script; decouples CI from local dev build hooks. |
| **Deprecate & Purge `asusd-user`** | ⏹️ **REOPEN / MERGE ([#310](https://github.com/OpenGamingCollective/asusctl/pull/310))** | 🟠 **P1** | Removes obsolete user daemon crate, dual services, and packaging bloat. |
| **Udev Worker & Mailbox Channel (`mio` Purge)** | 🟢 **APPROVED** | 🟠 **P1** | Replaces blocking `mio` threads in `aura_manager.rs` & `start_power_monitor` with a sync worker thread and Tokio `mpsc` mailbox; removes `mio` and nested Tokio runtimes without adding external stream crates. |
| **Unified Image Pipeline (`image`)** | 🔄 **PR OPEN ([#314](https://github.com/OpenGamingCollective/asusctl/pull/314))** | 🟠 **P1** | Unified PNG/APNG/GIF decoding under `image = "=0.25.9"`; purges `png_pong`, `pix`, `gif`, and `png`. |
| **AniMe Kernel I/O Decoupling** | 🔄 **PR OPEN ([#317](https://github.com/OpenGamingCollective/asusctl/pull/317))** | 🟠 **P1** | Decouples USB HID I/O with Condvar mailbox worker thread, FIFO queue, `&AnimeDataBuffer` zero-copy proxy, frame pre-computation. |
| **Armoury Validation & Persistence** | 🔄 **PR OPEN ([#300](https://github.com/OpenGamingCollective/asusctl/pull/300), [#301](https://github.com/OpenGamingCollective/asusctl/pull/301))** | 🟠 **P1** | Rejects invalid attribute values and simplifies JSON state serialization & boot restoration. |
| **Platform Profile per Power Source** | 🔄 **PR OPEN ([#316](https://github.com/OpenGamingCollective/asusctl/pull/316))** | 🟠 **P1** | Independent AC / Battery profile memory and automatic switching on power transitions. |
| **Missing ACPI Profile Fallback** | 🔄 **PR OPEN ([#280](https://github.com/OpenGamingCollective/asusctl/pull/280))** | 🟠 **P1** | Graceful fallback when firmware lacks Quiet/Low-Power profiles to prevent daemon crashes. |
| **Safe Config Loading (Read-Only)** | 🔄 **PR OPEN ([#305](https://github.com/OpenGamingCollective/asusctl/pull/305))** | 🟠 **P1** | Prevents crashes when reading configs on read-only filesystems or restricted permissions. |
| **`zerocopy`** | 🟢 **APPROVED (PoC Narrow)** | 🟠 **P1** | Type-safe USB HID 640-byte packet definition in `rog-anime` & `rog-aura`. |
| **Device Identity Engine (`dmi-id`)** | 🟢 **APPROVED** | 🟠 **P1** | Centralize DMI taxonomy & model parsing; eliminate duplicate `board_name` matching; add sysfs fallback & mockability. |
| **`argh` → `clap` (v4)** | 🟢 **APPROVED (Bench First)** | 🟠 **P1** | CLI overhaul for `asusctl` (subcommands, completions, validation). |
| **`strum`** | 🟢 **APPROVED (Targeted)** | 🟠 **P1** | Replaces duplicate string/enum matches for syntactic enums (`AuraModeNum`). |
| **`bitflags`** | 🟢 **APPROVED (Targeted)** | 🟠 **P1** | Typed bitmasks for hardware capability zones and power features. |
| **`human-panic` Crash Reports** | ⏹️ **REOPEN / MERGE ([#296](https://github.com/OpenGamingCollective/asusctl/pull/296))** | 🟡 **P2** | User-friendly crash dialogs and sanitized crash logs across binaries. |
| **Global Shortcuts Grab on Restore** | 🔄 **PR OPEN ([#312](https://github.com/OpenGamingCollective/asusctl/pull/312))** | 🟡 **P2** | Re-arms XDG global shortcut portals in `rog-control-center` upon desktop resume. |
| **`tracing`** | 🟢 **APPROVED (Phased)** | 🟡 **P2** | Structured async tracing for D-Bus requests, udev, and state transitions. |
| **`SysfsProvider` Mocking** | 🟢 **APPROVED** | 🟡 **P2** | Trait-based sysfs abstraction for non-root CI and hardware simulation. |
| **`tabled`** | ⚪ **OPTIONAL UX** | 🟡 **P2** | Formatted table output for `asusctl` CLI status commands. |
| **`procfs`** | ⚪ **TARGETED** | 🟡 **P2** | Replaces manual `/proc/` string parsing in `rog-platform` for CPU/thermal info. |
| **`tokio-util` (`CancellationToken`)** | 🟢 **APPROVED** | 🟠 **P1** | Replaces `AtomicBool` loops workspace-wide with `CancellationToken`; eliminates polling wakeups. |

# Major Refactoring & Architecture Modernization Specification for `asusctl`

This document details the comprehensive architectural refactoring, optimization, and modernization plan for the `asusctl` codebase (`asusd`, `asusctl`, `rog-control-center`, and associated sub-crates).

The primary goal of this initiative is **code simplification**, **elimination of async concurrency deadlocks**, **protocol safety**, **crate optimization**, and a **progressive transition toward kernel driver delegation**, establishing a robust, testable, and lightweight user-space policy orchestrator.

> **Commit Baseline**: Verified against `OpenGamingCollective/asusctl` at commit `2f5d4da67541483bd5adbff80fe431c8b29c003b`.  
> **Target MSRV**: **Rust 1.85** (unlocks `image = "^0.25"` and modern language features across workspace crates).

---

## 🎯 Executive Summary & Phased Strategy

Historically, `asusctl` accumulated custom user-space driver routines (raw WMI calls, raw HID packet crafting, custom powercap limit parsing) and nested concurrency locks (`Arc<Mutex<...>>`) to work around older Linux kernel limitations.

Because upstreaming kernel patches and migrating to new kernel drivers (e.g. `asus-armoury`, `asus-wmi`) is a long-term process tied to kernel release cycles, this refactoring plan adopts a **pragmatic two-track strategy**:

1. **Immediate User-Space Refactoring & Optimization**: Modernize daemon internals right now — eliminate nested `Arc<Mutex<...>>` locks via Tokio actors to fix D-Bus deadlocks, decouple code into a clean 3-layer architecture, streamline dependencies, migrate tooling to native Cargo workspace lints, and introduce `sysfs` provider traits for non-root CI testing.
2. **Progressive Kernel Offloading**: Opportunistically delegate low-level hardware driving to Linux kernel modules (`asus-wmi`, `asus-armoury`, `hid-asus`, `/sys/class/firmware_attributes/`) as modern kernel versions (7.0+) become widespread, keeping user-space fallback adapters modular.

---

## 🔒 Mandatory Governance & Engineering Invariants

All refactoring tasks and PRs must strictly comply with the following invariants:

1. **Rust 1.85 MSRV Target**: Workspace MSRV is updated to **Rust 1.85**. Dependencies requiring 1.85 (e.g. `image = "^0.25"`) are fully unblocked.
2. **Measurement-Driven Execution**: No performance claim is valid without before/after benchmarks. Optimization priority belongs strictly to clean/incremental build times, binary size (`.text` section), RSS memory, timer wakeups (`powertop`), and protocol correctness.
3. **LOC is an Observation, Not a KPI**: Source LOC reduction is recorded for maintainability reporting only. No task may be approved or rejected based on LOC delta alone.
4. **Zero `.unwrap()` Prohibition**: Never use `.unwrap()` in production code. Use proper error propagation (`?`), pattern matching, or `.expect("Clear explanation of invariant")`.
5. **Strict `unsafe` Control**: Avoid `unsafe` blocks whenever safe Rust abstractions exist. Any mandatory `unsafe` block MUST be preceded by a mandatory `// SAFETY:` doc comment explaining memory safety invariants.
6. **D-Bus Backward Compatibility**: Preserve existing D-Bus method signatures and object paths (`/org/asuslinux/...`) so external clients (`rog-control-center`, GNOME extensions) continue functioning seamlessly.
7. **Native Cargo Workspace Lints**: External lint tools (`Cranky.toml`) are retired in favor of native `[workspace.lints]` in root `Cargo.toml`.

---

## 🗺️ Implementation Roadmap

```text
┌──────────────────────────────────────────────────────────────────────────┐
│ Phase 0: Baseline Benchmark Harness & Environment Setup                  │
├──────────────────────────────────────────────────────────────────────────┤
│  ├── 0.1 Reproducible Profiling Protocol (Build time, .text size, RSS)   │
│  └── 0.2 Workspace MSRV 1.85 Migration Target Setup                      │
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
│  └── 2.3 Armoury Attribute Management (Pub/Sub Event System)             │
└───────────────────────────────────┬──────────────────────────────────────┘
                                    │
                                    ▼
┌───────────────────────────────────────────────────────────────────────────┐
│ Phase 3: Protocol Safety, Ergonomics, Event Loop & CLI                    │
├───────────────────────────────────────────────────────────────────────────┤
│  ├── 3.1 USB HID Wire Protocol Safety (`zerocopy`)                        │
│  ├── 3.2 PNG & Raster Pipeline Modernization (`rog-anime` image migration)│
│  ├── 3.3 Async Hardware Event Stream (`tokio-udev` & Lifecycle Tokens)    │
│  ├── 3.4 Ergonomic Types & CLI Modernization (`clap` v4, `strum`, flags)  │
│  └── 3.5 Strongly-Typed Domain Error Hierarchy (`thiserror` v2)           │
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

### 0.2 Workspace MSRV 1.85 Target
* Set `rust-version = "1.85"` in root `Cargo.toml`.
* Unblocks modern crate versions such as `image = "^0.25"` for raster/animation decoders without requiring legacy version workarounds.

---

## Phase 1: Immediate User-Space Concurrency & Tooling Modernization

### 1.1 State Architecture: Actor Model (Lock Elimination for Deadlock Prevention)

* **Current Issue**: The daemon relies heavily on nested asynchronous concurrent locks (`Arc<Mutex<AuraConfig>>`, `Arc<Mutex<HidRaw>>`, `Arc<Mutex<HashMap<...>>>`). In `aura_manager.rs`, structures like `Arc<Mutex<HashMap<String, Arc<Mutex<HidRaw>>>>>` can cause D-Bus calls to deadlock asynchronously at startup or reload.
* **Refactoring Proposal**: Transition hardware controllers to a message-driven model (actor style). Each controller is managed by a dedicated Tokio async task that exclusively owns its state, communicating via unidirectional channels (`tokio::sync::mpsc`).
* **Target Benefits**:
  * Total elimination of concurrency blocking and D-Bus deadlocks.
  * Clean, predictable execution flow.
  * Simplifies unit testing by allowing mock channel receivers.

### 1.2 Tooling Modernization: `Cranky.toml` → Native `[workspace.lints]`

* **Current Issue**: The repository uses an external wrapper configuration (`Cranky.toml`, 118 lines, 107 clippy error overrides) rather than standard Cargo workspace lint inheritance.
* **Refactoring Proposal**: Migrate all clippy, rustc, and rustdoc policy rules directly into `[workspace.lints.clippy]`, `[workspace.lints.rust]`, and `[workspace.lints.rustdoc]` in root `Cargo.toml`. Member crates inherit policy via `[lints] workspace = true`.
* **Target Benefits**: Zero reliance on external binary wrappers; standard `cargo clippy` and `cargo check` enforce workspace-wide lint compliance.

### 1.3 Git Hook Infrastructure: `cargo-husky` → Native `.githooks`

* **Current Issue**: `cargo-husky` adds build-script overhead to dev dependencies for copying git hooks on build.
* **Refactoring Proposal**: Replace `cargo-husky` with native git hooks stored in `.githooks/` and configured via `git config core.hooksPath .githooks`. Ensure CI execution is completely independent of local developer git hooks.

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

### 2.3 Armoury Attribute Management (Schema-Driven & Event Synchronization)

* **Current Issue**: Settings in `asus_armoury.rs` rely on hardcoded attribute paths and conditional branches (`if/match`). For example, Intel RAPL limits require custom logic injected directly inside generic attribute write functions.
* **Refactoring Proposal**: Define a Publisher-Subscriber event system for firmware attributes:
  * All attributes are enumerated in a centralized registry at boot.
  * Any attribute update emits an asynchronous `AttributeChanged` event.
  * Decoupled subscriber modules (e.g. `IntelPowerSync`) listen to events and handle side-effects without polluting core attribute logic.

---

## Phase 3: Protocol Safety, Ergonomics, Event Loop & CLI

### 3.1 USB HID Wire Protocol Safety (`zerocopy`)

* **Current Issue**: `rog-anime` and `rog-aura` construct 640-byte USB HID packets (`pub type AnimePacketType = Vec<[u8; 640]>`) using manual byte slicing and index offset calculations.
* **Refactoring Proposal**: Use `zerocopy` to define strongly-typed HID packet header and payload structures using `#[repr(C)]` with explicit endian types (`U16<LittleEndian>`, `U32<LittleEndian>`) and `Unaligned`.
* **Target Benefits**:
  * Eliminates out-of-bounds slicing crashes.
  * Zero-cost serialization/deserialization validated against byte-for-byte golden wire tests.

### 3.2 PNG & Raster Pipeline Modernization (`rog-anime`)

* **Current Issue**: Image processing in `rog-anime` relies on `png_pong` for decoding and `pix::Raster` for color conversions, adding redundant intermediate abstractions.
* **Refactoring Proposal**: With Rust 1.85 MSRV, replace `png_pong` and `pix` simultaneously with `image` (`^0.25`). Map decoders directly from PNG/APNG to `Vec<Pixel>` for `AnimeImage`.
* **Target Benefits**:
  * Consolidates image decoding into a single well-maintained dependency.
  * Verified against golden pixel oracle tests for color luminance, alpha blending, and APNG frame compositing.

### 3.3 Async Hardware Event Stream & Task Lifecycle

* **Current Issue**: `aura_manager.rs:L526` spawns a blocking thread running `mio` on udev and instantiates a secondary Tokio runtime (`rt.block_on`) inside the loop.
* **Refactoring Proposal**:
  * Adopt `tokio-udev` (or native non-blocking async udev monitor streams) directly on the daemon's Tokio event loop.
  * Evaluate `tokio-util::sync::CancellationToken` for clean task cancellation during device hot-unplug and daemon reloads.
* **Target Benefits**: Eliminates dedicated blocking OS threads and secondary runtime instantiations.

### 3.4 Ergonomic Types & CLI Modernization

* **CLI Framework (`asusctl`)**: Migrate from `argh` to `clap` (v4 with derive) for improved subcommands, value validation, interactive table rendering (`tabled`), shell completions (`clap_complete`), and man pages.
* **Enum Conversions (`strum`)**: Apply `strum` to purely syntactic string-to-enum conversions (e.g. `AuraModeNum`).
* **Hardware Capability Flags (`bitflags`)**: Replace raw capability integers and boolean flags with strongly-typed `bitflags` structs for keyboard lighting zones and power modes.
* **Procfs Reading (`rog-platform`)**: Replace manual string parsing loops in `/proc/` with `procfs` for reading CPU and thermal information.

### 3.5 Strongly-Typed Domain Error Hierarchy (`thiserror` v2 Uniformity)

* **Current Issue**: Error handling frequently stringifies errors (`RogError::Error(String)`) or uses generic wrappers, discarding context.
* **Refactoring Proposal**: Standardize strongly-typed domain errors per subsystem (e.g. `PowerError::SysfsWriteFailed { path, source }`, `AuraError::DeviceDisconnected`) using `thiserror` v2 across all workspace crates.
* **Target Benefits**: Graceful degradation on hardware failures without crashing the daemon; clear D-Bus error messages.

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

### Controller Traits

* **`GetSupported`**: Checks hardware/kernel features before controller initialization.
* **`Reloadable`**: Reloads configuration and state dynamically without restarting `asusd`.
* **`CtrlTask`**: Runs background tasks, monitors system signals (suspend/resume/boot), and watches configuration paths.
* **`ZbusAdd`**: Exposes controller interfaces cleanly on the system bus via `zbus`.

### Lock Elimination Guidelines

1. Avoid wrapping controllers in `Arc<Mutex<T>>`.
2. Route external D-Bus invocations and background tasks through Tokio `mpsc` channels to an actor task owning the controller.
3. If an async lock is strictly required in legacy task loops, use non-blocking `try_lock()` inside task event callbacks to prevent deadlocks when system events fire concurrently.

---

## 📊 Summary Matrix of Approved Workspace Crate Improvements

| Improvement / Candidate Crate | Status / Scope | Priority | Target Benefit |
| :--- | :---: | :---: | :--- |
| **`[workspace.lints.clippy]`** | 🟢 **APPROVED** | 🔴 **P0** | Native Cargo workspace lint policy replacing `Cranky.toml`. |
| **`cargo-husky` → `.githooks`** | 🟢 **APPROVED** | 🟠 **P1** | Native git hooks script; decouples CI from local dev build hooks. |
| **`png_pong` + `pix` → `image`** | 🟢 **APPROVED (Rust 1.85)** | 🟠 **P1** | Unified PNG/APNG decoding in `rog-anime` using `image = "^0.25"`. Removes `pix`. |
| **`zerocopy`** | 🟢 **APPROVED (PoC Narrow)** | 🟠 **P1** | Type-safe USB HID 640-byte packet definition in `rog-anime` & `rog-aura`. |
| **`argh` → `clap` (v4)** | 🟢 **APPROVED (Bench First)** | 🟠 **P1** | CLI overhaul for `asusctl` (subcommands, completions, validation). |
| **`strum`** | 🟢 **APPROVED (Targeted)** | 🟠 **P1** | Replaces duplicate string/enum matches for syntactic enums (`AuraModeNum`). |
| **`bitflags`** | 🟢 **APPROVED (Targeted)** | 🟠 **P1** | Typed bitmasks for hardware capability zones and power features. |
| **`tracing`** | 🟢 **APPROVED (Phased)** | 🟡 **P2** | Structured async tracing for D-Bus requests, udev, and state transitions. |
| **`tabled`** | ⚪ **OPTIONAL UX** | 🟡 **P2** | Formatted table output for `asusctl` CLI status commands. |
| **`procfs`** | ⚪ **TARGETED** | 🟡 **P2** | Replaces manual `/proc/` string parsing in `rog-platform` for CPU/thermal info. |
| **`tokio-util`** | ⚪ **TARGETED** | 🟡 **P2** | `CancellationToken` for clean task cancellation during device hot-unplug and reload. |

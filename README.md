# Major Refactoring & Architecture Modernization Specification for `asusctl`

This document details the architectural refactoring plan for the `asusctl` codebase (`asusd`, `asusctl`, `rog-control-center`, and associated sub-crates). The primary goal of this initiative is **code simplification**, **elimination of async concurrency deadlocks**, and a **progressive transition toward kernel driver delegation**, establishing a robust, testable user-space policy orchestrator.

---

## 🎯 Executive Summary & Phased Strategy

Historically, `asusctl` accumulated custom user-space driver routines (raw WMI calls, raw HID packet crafting, custom powercap limit parsing) and nested concurrency locks (`Arc<Mutex<...>>`) to work around older Linux kernel limitations.

Because upstreaming kernel patches and migrating to new kernel drivers (e.g. `asus-armoury`, `asus-wmi`) is a long-term process tied to kernel release cycles, this refactoring plan adopts a **pragmatic two-track strategy**:

1. **Immediate User-Space Refactoring (Short-Term Focus)**: Modernize daemon internals right now — eliminate nested `Arc<Mutex<...>>` locks via Tokio actors to fix D-Bus deadlocks, decouple code into a clean 3-layer architecture, simplify redundant helper logic, and introduce sysfs provider traits for non-root CI testing.
2. **Progressive Kernel Offloading (Long-Term Phased Transition)**: Opportunistically delegate low-level hardware driving to Linux kernel modules (`asus-wmi`, `asus-armoury`, `hid-asus`, `/sys/class/firmware_attributes/`) as modern kernel versions (6.19+) become widespread, keeping user-space fallback adapters modular.

---

## 🗺️ Implementation Roadmap

```text
┌────────────────────────────────────────────────────────────────────────┐
│ Phase 1: Immediate User-Space Concurrency & Code Cleanup               │
├────────────────────────────────────────────────────────────────────────┤
│  ├── 1.1 State Architecture: Actor Model (Lock Elimination)            │
│  └── 1.2 Codebase & Crate Simplification                               │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ Phase 2: Architectural Decoupling & Gradual Kernel Offloading          │
├────────────────────────────────────────────────────────────────────────┤
│  ├── 2.1 Driver vs Daemon Decoupling (3-Layer Architecture)            │
│  ├── 2.2 Progressive Kernel Offloading & Driver Delegation             │
│  └── 2.3 Armoury Attribute Management (Pub/Sub Event System)           │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ Phase 3: Hardware Event Handling & Domain Error Robustness             │
├────────────────────────────────────────────────────────────────────────┤
│  ├── 3.1 Hardware Event Handling (Async udev Stream Handling)          │
│  └── 3.2 Strongly-Typed Domain Error Hierarchy (`thiserror`)           │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ Phase 4: Testability, Observability & Automation                       │
├────────────────────────────────────────────────────────────────────────┤
│  ├── 4.1 `sysfs` Abstraction & Hardware Mocking (`SysfsProvider`)      │
│  ├── 4.2 Asynchronous Observability & Structured Tracing (`tracing`)   │
│  └── 4.3 Automated Integration Testing Suite (`uhid-virt` & E2E)       │
└────────────────────────────────────────────────────────────────────────┘
```

---

## Phase 1: Immediate User-Space Concurrency & Code Cleanup (Immediate Precedence)

### 1.1 State Architecture: Actor Model (Lock Elimination for Deadlock Prevention)

* **Current Issue**: The daemon relies heavily on nested asynchronous concurrent locks (`Arc<Mutex<AuraConfig>>`, `Arc<Mutex<HidRaw>>`, `Arc<Mutex<HashMap<...>>>`). This design makes D-Bus calls prone to unpredictable asynchronous deadlocks at startup or reload.
* **Refactoring Proposal**: Transition hardware controllers to a message-driven model (actor style). Each controller is managed by a dedicated Tokio async task that exclusively owns its state, communicating via unidirectional channels (`tokio::sync::mpsc`).
* **Target Benefits**:
  * Total elimination of concurrency blocking and D-Bus deadlocks.
  * Clean, predictable execution flow.
  * Simplifies unit testing by allowing mock channel receivers.

---

### 1.2 Codebase & Crate Simplification

* **Current Issue**: The workspace contains redundant abstraction layers and duplicate helper functions across `rog-platform`, `rog-aura`, and `asusd`.
* **Refactoring Proposal**:
  * Consolidate redundant helper functions and strip out obsolete user-space driver routines.
  * Simplify inter-crate API surfaces to reduce compilation times and binary footprint.
* **Target Benefits**:
  * Significant reduction in workspace binary sizes and compilation overhead.
  * Clean, minimal code paths and improved maintainability across sub-crates.

---

## Phase 2: Architectural Decoupling & Gradual Kernel Offloading

### 2.1 Driver vs Daemon Decoupling (3-Layer Architecture)

* **Current Issue**: Low-level hardware driving logic is tightly coupled within `asusd` alongside D-Bus service logic and configuration serialization formats.
* **Refactoring Proposal**: Structurally split the codebase into three distinct layers:
  1. **Driver/Kernel Adaptor Layer**: Standalone modules interfacing with kernel sysfs/WMI interfaces or fallback USB/HID communication.
  2. **Core Engine (Policy & State)**: The actual daemon, which decides behavioral policies, applies user preferences, and responds to system state changes (power supply, suspend, throttling profiles).
  3. **IPC Layer (D-Bus Interfaces)**: A thin layer exposing D-Bus interfaces via `zbus` and translating remote calls into commands for the Core Engine.

---

### 2.2 Progressive Kernel Offloading & Driver Delegation

* **Current Issue**: Custom user-space WMI/HID driver routines require ongoing maintenance for each new laptop generation. Upstreaming native kernel drivers takes time, requiring a phased transition.
* **Refactoring Proposal**:
  * Detect available kernel interfaces (`asus-armoury`, `asus-wmi`, `/sys/class/firmware_attributes/`) at boot via `GetSupported`.
  * Offload hardware operations (e.g. power limits, fan curves, BIOS attributes) to native kernel nodes when present.
  * Maintain clean, isolated user-space fallback adapters in the Adaptor Layer for older kernels, phasing them out gradually as native kernel driver adoption matures.
* **Target Benefits**:
  * Progressive code cleanup without breaking hardware compatibility on older kernels.
  * Seamless transition to kernel-native interfaces as users update their kernels.

---

### 2.3 Armoury Attribute Management (Schema-Driven & Event Synchronization)

* **Current Issue**: Settings in `asus_armoury.rs` rely on hardcoded attribute paths and conditional branches (`if/match`). For example, Intel RAPL limits require custom logic injected directly inside generic attribute write functions.
* **Refactoring Proposal**: Define a Publisher-Subscriber event system for firmware attributes:
  * All attributes are enumerated in a centralized registry at boot.
  * Any attribute update emits an asynchronous `AttributeChanged` event.
  * Decoupled subscriber modules (e.g. `IntelPowerSync`) listen to events and handle side-effects without polluting core attribute logic.

---

## Phase 3: Hardware Event Handling & Domain Error Robustness

### 3.1 Hardware Event Handling (Async udev Stream Handling)

* **Current Issue**: In `aura_manager.rs`, a synchronous native system thread (`std::thread::spawn`) runs a blocking polling loop via `mio` on udev, repeatedly creating and destroying a Tokio runtime inside the loop.
* **Refactoring Proposal**: Adopt `tokio-udev` (or native non-blocking async udev monitor streams).
* **Target Benefits**:
  * HID and SCSI device hotplug/unplug events are processed as a standard async `Stream` inside the daemon event loop.
  * Eliminates blocking OS threads and secondary Tokio runtime instantiations.

---

### 3.2 Strongly-Typed Domain Error Hierarchy (`thiserror` Uniformity)

* **Current Issue**: Error handling frequently stringifies errors (`RogError::Error(String)`) or uses generic wrappers, discarding context (e.g. specific sysfs path or hardware failure cause).
* **Refactoring Proposal**: Define strongly-typed domain errors per subsystem (e.g. `PowerError::SysfsWriteFailed { path, source }`, `AuraError::DeviceDisconnected`) using `thiserror` across all crates.
* **Target Benefits**:
  * Graceful degradation on hardware failures without crashing the daemon.
  * Clearer, actionable D-Bus error messages returned to clients.

---

## Phase 4: Testability, Observability & Automation

### 4.1 `sysfs` Abstraction & Hardware Mocking (Testability without ASUS Hardware)

* **Current Issue**: Direct `std::fs::write` and `read_to_string` calls are scattered across `asusd` and `rog-platform` (e.g. `/sys/class/powercap`, `/sys/devices/platform/asus-nb-wmi/`). This prevents unit/integration testing on CI or non-ASUS machines.
* **Refactoring Proposal**: Introduce a `SysfsProvider` trait (`RealSysfs` for daemon runtime, `MockSysfs` for test environments).
* **Target Benefits**:
  * Full test coverage of daemon profile logic and Armoury attribute management without requiring root privileges or physical hardware.
  * Reliable CI test execution.

---

### 4.2 Asynchronous Observability & Structured Tracing (`tracing` Migration)

* **Current Issue**: `asusd` handles concurrent async events (D-Bus requests, udev hotplug, AC adapter state changes, system suspend/resume) using the standard `log` crate (`log::info!`, `log::warn!`), making it difficult to trace async task execution flows across channels.
* **Refactoring Proposal**: Migrate from `log` to `tracing` and `tracing-subscriber`, using structured spans for D-Bus calls and state transitions.
* **Target Benefits**:
  * Instant identification of async deadlocks, request timeouts, and state transition races.
  * Structured log output compatible with `systemd-journald`.

---

### 4.3 Automated Integration Testing Suite (`uhid-virt` & Simulators)

* **Current Issue**: The repository includes a `simulators` crate, but lacks an automated E2E integration test suite that spawns `asusd` against a test D-Bus session.
* **Refactoring Proposal**: Create an integration test runner using `uhid-virt` and virtual D-Bus session buses to test `asusctl` CLI commands against a live daemon instance.
* **Target Benefits**: Prevents regressions during major refactoring of IPC layers and state architecture.

---

## 🛠️ Daemon Architecture & Design Patterns

When refactoring daemon components, the following architectural patterns must be preserved and updated to actor/task abstractions:

### Controller Traits

* **`GetSupported`**: Checks hardware/kernel features before controller initialization.
* **`Reloadable`**: Reloads configuration and state dynamically without restarting `asusd`.
* **`CtrlTask`**: Runs background tasks, monitors system signals (suspend/resume/boot), and watches configuration paths.
* **`ZbusAdd`**: Exposes controller interfaces cleanly on the system bus via `zbus`.

### Lock Elimination Guidelines

When refactoring shared controller state:
1. Avoid wrapping controllers in `Arc<Mutex<T>>` where possible.
2. Route external D-Bus invocations and background tasks through Tokio mpsc channels to an actor task owning the controller.
3. If an async lock is strictly required in legacy task loops, use non-blocking `try_lock()` inside task event callbacks to prevent deadlocks when system events fire concurrently.

---

## 📏 Repository Engineering Rules & Refactoring Standards

All refactoring commits must strictly comply with the following standards:

1. **Zero `.unwrap()` Prohibition**: Never use `.unwrap()` in production code. Use proper error propagation (`?`), pattern matching, or `.expect("Clear explanation of invariant")`.
2. **Strict `unsafe` Control**: Avoid `unsafe` blocks whenever safe Rust abstractions exist. Any mandatory `unsafe` block (e.g. kernel ioctls or raw FFI) MUST be preceded by a mandatory `// SAFETY:` doc comment explaining memory safety invariants.
3. **D-Bus Backward Compatibility**: Preserve existing D-Bus method signatures and object paths (`/org/asuslinux/...`) so external clients (`rog-control-center`, GNOME extensions) continue functioning seamlessly.
4. **Sysfs Attribute Resilience**: Always verify sysfs path existence before reading/writing and parse/validate all inputs/outputs safely without crashing.
5. **Safe Config Schema Maintenance**: Provide `Default` implementations for configuration structs and ensure robust error handling during configuration deserialization.
6. **No Symptom Patching**: Resolve errors by fixing underlying root causes in hardware interactions or task orchestration rather than swallowing exceptions.
7. **Clean Verification**: All commits must pass local verification checks cleanly:
   * `cargo fmt --all -- --check`
   * `cargo clippy --all -- -D warnings`
   * `cargo cranky`
   * `cargo test --all`

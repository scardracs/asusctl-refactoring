#!/usr/bin/env python3
"""
Sync Upstream Status Script for asusctl-refactoring.

Fetches open and closed pull requests and issues from OpenGamingCollective/asusctl
and regenerates PULL_REQUESTS.md and ISSUES.md.
"""

import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone

REPO = "OpenGamingCollective/asusctl"
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")

def fetch_github_api(endpoint: str, params: dict = None) -> list:
    """Fetch paginated data from GitHub API."""
    query_str = "&".join(f"{k}={v}" for k, v in (params or {}).items())
    url = f"https://api.github.com/repos/{REPO}/{endpoint}"
    if query_str:
        url += f"?{query_str}"

    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "asusctl-refactoring-sync-bot",
    }
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"

    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data if isinstance(data, list) else [data]
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code} for {url}: {e.reason}", file=sys.stderr)
        return []
    except Exception as e:
        print(f"Error fetching {url}: {e}", file=sys.stderr)
        return []

def get_all_prs():
    """Fetch open and recently closed PRs."""
    open_prs = fetch_github_api("pulls", {"state": "open", "per_page": 50})
    closed_prs = fetch_github_api("pulls", {"state": "closed", "per_page": 50})
    return open_prs, closed_prs

def get_all_issues():
    """Fetch open and recently closed issues (excluding PRs)."""
    open_issues = fetch_github_api("issues", {"state": "open", "per_page": 100})
    closed_issues = fetch_github_api("issues", {"state": "closed", "per_page": 50})

    # Filter out pull requests which GitHub API includes in /issues
    open_issues = [i for i in open_issues if "pull_request" not in i]
    closed_issues = [i for i in closed_issues if "pull_request" not in i]
    return open_issues, closed_issues

def assess_pr(pr: dict) -> tuple[str, str, str]:
    """Return status icon, recommended action, and roadmap phase for PR."""
    num = pr["number"]
    title = pr.get("title", "")
    is_merged = pr.get("merged_at") is not None
    state = pr.get("state", "open")

    # Known roadmap mapping
    roadmap_map = {
        317: ("🟢 KEEP / MERGE: Reference implementation for 'Async Control, Sync Data'", "Phase 1.1"),
        316: ("🟢 KEEP / MERGE: Dynamic AC vs Battery platform profile memory", "Phase 2.5"),
        314: ("🟢 KEEP / MERGE: Consolidated image pipeline under image = '=0.25.9'", "Phase 3.2"),
        312: ("🟢 KEEP / MERGE: Re-arms XDG Global Shortcuts portal upon desktop resume", "Phase 3.3"),
        310: ("🟠 REOPEN / MERGE: Purges obsolete asusd-user crate, units, and packaging bloat", "Phase 1.4"),
        311: ("🟠 REOPEN / MERGE: Purges legacy examples and unneeded check/test targets", "Phase 3.4"),
        305: ("🟢 KEEP / MERGE: Prevents panics on read-only configs (Invariant #5)", "Phase 3.4"),
        301: ("🟢 KEEP / MERGE: Simplifies Armoury attribute persistence & boot restoration", "Phase 2.3"),
        300: ("🟢 KEEP / MERGE: Rejects out-of-bounds Armoury tuning writes to sysfs", "Phase 2.3"),
        296: ("🟠 REOPEN / MERGE: User-friendly crash dialogs & sanitized logs across CLI/GUI", "Phase 3.4"),
        280: ("🟢 KEEP / MERGE: Graceful fallback when firmware lacks Quiet/Low-Power profile", "Phase 2.5"),
        315: ("Merged into rogcc-redesign: Prepares modular pages & accessibility", "Phase 3.4"),
        309: ("Integrated Upstream (6b6cdc63): Migrated workspace to Rust Edition 2024", "Phase 0.2"),
        308: ("Integrated Upstream (84645b6a): Upgraded MSRV to Rust 1.85.0", "Phase 0.2"),
        307: ("Integrated Upstream (a1322ff9): Added Aura support for ROG Strix G16 G614PP", "Phase 2.4"),
        306: ("Integrated Upstream (31635a6f): Eliminated nested Tokio runtime startup panics", "Phase 1.1"),
        303: ("Integrated Upstream (5307fd13): Major documentation overhaul & CLI guide", "Phase 4"),
        299: ("Integrated Upstream (48daeaab): Adapted XDG shortcuts to KDE portal lifecycle", "Phase 3.3"),
        298: ("Integrated Upstream (dfe4185b): Reinstated committed Cargo.lock", "Phase 0.2"),
        297: ("Integrated Upstream (f1691584): Event-driven logind-zbus & power monitoring", "Phase 1.1"),
        294: ("Integrated Upstream (731d772c): Passive zero-wakeup dGPU telemetry & udev scan deduplication", "Phase 1.1"),
    }

    if num in roadmap_map:
        action, phase = roadmap_map[num]
        if is_merged:
            status = "✅ **MERGED**"
        elif state == "closed":
            status = "⏹️ **CLOSED**"
        else:
            status = "🔄 **OPEN**"
        return status, action, phase

    if is_merged:
        return "✅ **MERGED**", "Integrated Upstream", "Phase 2 / 3"
    elif state == "closed":
        return "⏹️ **CLOSED**", "Review for relevance", "Phase 2 / 3"
    else:
        return "🔄 **OPEN**", "Evaluate for roadmap integration", "Phase 2 / 3"

def generate_pull_requests_md(open_prs: list, closed_prs: list) -> str:
    """Generate markdown content for PULL_REQUESTS.md."""
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    # Combine key PRs in priority order
    all_prs = open_prs + [p for p in closed_prs if p.get("merged_at") or p["number"] in (310, 311, 296)]
    # Deduplicate by number
    seen = set()
    unique_prs = []
    for pr in all_prs:
        if pr["number"] not in seen:
            seen.add(pr["number"])
            unique_prs.append(pr)

    unique_prs.sort(key=lambda p: p["number"], reverse=True)

    md = [
        "# 🔀 Pull Request Catalog & Architectural Assessment",
        "",
        f"> *Last automated synchronization: {now_str}*",
        "",
        f"This document provides an automated audit of upstream pull requests (Open, Merged, and Closed-without-merge) from [`{REPO}`](https://github.com/{REPO}/pulls).",
        "",
        "Each pull request is evaluated for its architectural impact, alignment with the **\"Async Control, Sync Data\"** paradigm, dependency health, and whether it should be merged, kept, or reopened.",
        "",
        "---",
        "",
        "## 📑 Summary Matrix",
        "",
        "| PR # | Type / Area | Branch / Scope | Status | Recommended Action | Roadmap Phase |",
        "| :--- | :--- | :--- | :---: | :--- | :---: |",
    ]

    for pr in unique_prs:
        num = pr["number"]
        title = pr.get("title", "").replace("|", "\\|")
        branch = pr.get("head", {}).get("ref", "unknown")
        url = pr.get("html_url", f"https://github.com/{REPO}/pull/{num}")
        status, action, phase = assess_pr(pr)
        md.append(f"| **[#{num}]({url})** | `{title[:40]}...` | `{branch}` | {status} | **{action}** | {phase} |")

    md.extend([
        "",
        "---",
        "",
        "## 🔍 Detailed Analysis of Critical Pull Requests",
        "",
        "### 1. PR #317: AniMe Kernel I/O Decoupling & Zero-Copy Proxy",
        "* **Scope**: `asusd::aura_anime`, `rog-anime`, `rog-dbus`",
        "* **Branch**: `perf/anime-io-pipeline`",
        "* **Status**: 🔄 Open (Active development)",
        "* **Architectural Value**:",
        "  * Decouples synchronous, blocking USB HID packet writes (`rusb` / `/dev/hidraw`) from Tokio's async reactor via a dedicated OS thread and an `Arc<Condvar>` single-slot mailbox.",
        "  * Replaces expensive D-Bus payload clones with zero-copy `&AnimeDataBuffer` IPC methods in `rog-dbus`.",
        "  * Pre-computes frame diagonals off the event loop, eliminating D-Bus request timeouts and desktop stutter during intensive AniMe Matrix playback.",
        "* **Recommendation**: **🟢 Merge Immediately** as the reference pattern for all hardware controllers.",
        "",
        "---",
        "",
        "### 2. PR #310: Remove Obsolete `asusd-user` Crate & Services",
        "* **Scope**: Workspace root, `asusd-user/`, `data/asusd-user.service`, `Makefile`, `PKGBUILD`",
        "* **Branch**: `refactor/remove-asusd-user`",
        "* **Status**: ⏹️ Closed without merge (Closed temporarily during Rust 1.85 migration)",
        "* **Architectural Value**:",
        "  * `asusd-user` is redundant: all features (Aura, AniMe, Armoury, fan curves) are natively served on the system D-Bus by `asusd`.",
        "  * All active clients (`asusctl`, `rog-control-center`, desktop extensions) connect solely to the system bus.",
        "  * Dual daemons cause significant user confusion and packaging headaches across Arch, Fedora, Debian, and Ubuntu.",
        "* **Recommendation**: **🟠 Reopen & Merge**. Includes packaging cleanup hooks (`cleanup_asusd_leftovers`) to remove legacy user services upon package upgrade.",
        "",
        "---",
        "",
        "### 3. PR #314: Unified Image & Animation Decoding Pipeline",
        "* **Scope**: `rog-anime`, `asusctl`, workspace `Cargo.toml`",
        "* **Branch**: `refactor/unify-image-crate`",
        "* **Status**: 🔄 Open",
        "* **Architectural Value**:",
        "  * Purges 4 redundant crates: `png_pong`, `pix`, standalone `gif`, and standalone `png`.",
        "  * Standardizes image and animation decoding under `image = \"=0.25.9\"`.",
        "  * Fixes subframe canvas coordinate conversion regressions for animated GIF and APNG frames.",
        "* **Recommendation**: **🟢 Merge Immediately**.",
        "",
        "---",
        "",
        "### 4. PR #316: Platform Profile Memory Per Power Source (AC vs Battery)",
        "* **Scope**: `asusd`, `rog-profiles`, `rog-platform`",
        "* **Branch**: `feature/profile-per-source`",
        "* **Status**: 🔄 Open",
        "* **Architectural Value**:",
        "  * Solves a long-standing user request: allows setting 'Performance' when plugged into AC and 'Quiet' when running on Battery.",
        "  * Automatically switches between remembered profiles upon receiving power supply transition signals from `logind-zbus`.",
        "* **Recommendation**: **🟢 Merge**.",
        "",
        "---",
        "",
        "### 5. PR #300 & PR #301: Armoury Tuning Validation & Simplified Persistence",
        "* **Scope**: `asusd`, `rog-platform`",
        "* **Branches**: `fix/armoury-tuning-validation`, `refactor/armoury-persistence`",
        "* **Status**: 🔄 Open",
        "* **Architectural Value**:",
        "  * **PR #300**: Validates Armoury attribute values against hardware bounds before writing to sysfs, preventing crashes on unsupported tunables.",
        "  * **PR #301**: Normalizes JSON state serialization in `/var/lib/asusd/armoury.json` with self-healing fallback when loading configs on newly updated kernels.",
        "* **Recommendation**: **🟢 Merge Both** in sequence.",
        "",
        "---",
        "",
        "### 6. PR #305: Safe Configuration Loading Without Panicking",
        "* **Scope**: `config-traits`",
        "* **Branch**: `fix/config-traits-read-only`",
        "* **Status**: 🔄 Open",
        "* **Architectural Value**:",
        "  * Fixes Issue #304. Prevents `.unwrap()` crashes when configuration files are accessed with read-only permissions or in restricted container environments.",
        "* **Recommendation**: **🟢 Merge**. Enforces Engineering Invariant #5 (Zero `.unwrap()`).",
        "",
        "---",
        "",
        "### 7. PR #296: Integrated Crash Reporting with `human-panic`",
        "* **Scope**: `asusctl`, `rog-control-center`, `asusd`",
        "* **Branch**: `feature/human-panic`",
        "* **Status**: ⏹️ Closed",
        "* **Architectural Value**:",
        "  * Intercepts unhandled panics across CLI and GUI tools to display clear, actionable crash dialogs and generate sanitized crash report files for bug reporting.",
        "* **Recommendation**: **🟠 Reopen & Merge**.",
        "",
        "---",
        "",
        "### 8. PR #311: Purge Obsolete Examples & Dev-Dependencies",
        "* **Scope**: `asusctl/examples/`, `asusctl/Cargo.toml`",
        "* **Branch**: `chore/remove-asusctl-examples`",
        "* **Status**: ⏹️ Closed",
        "* **Architectural Value**:",
        "  * Removes outdated example scripts referencing legacy `png` dependencies, reducing compilation time and clutter in `cargo test --all-targets`.",
        "* **Recommendation**: **🟠 Reopen & Merge**.",
        "",
        "---",
        "",
        "## 🔗 Cross References",
        "",
        "* Main Architectural Plan: [README.md](README.md)",
        "* Comprehensive Issues Audit: [ISSUES.md](ISSUES.md)",
        "",
    ])

    return "\n".join(md)

def categorize_issue(issue: dict) -> str:
    """Classify issue into one of 6 functional categories."""
    title = issue.get("title", "").lower()
    labels = [l["name"].lower() for l in issue.get("labels", [])]
    body = (issue.get("body") or "").lower()

    if any(k in title or k in labels for k in ["power", "gpu", "dgpu", "igpu", "nvml", "battery", "charge", "fan", "curve", "thermal", "throttle"]):
        return "power"
    elif any(k in title or k in labels for k in ["deadlock", "lock", "concurrency", "dbus", "leak", "poll", "loop", "logind", "hotplug", "task"]):
        return "concurrency"
    elif any(k in title or k in labels for k in ["panic", "crash", "unwrap", "freeze", "abort", "segmentation", "read-only"]):
        return "crashes"
    elif any(k in title or k in labels for k in ["keyboard", "aura", "led", "backlight", "rgb", "lamparray", "dmi", "quirk", "touchpad", "scsi", "device-support"]):
        return "hardware"
    elif any(k in title or k in labels for k in ["ui", "gui", "rog-control-center", "window", "cli", "asusctl", "shortcut", "slint", "theme"]):
        return "gui_cli"
    else:
        return "packaging_docs"

def generate_issues_md(open_issues: list, closed_issues: list) -> str:
    """Generate markdown content for ISSUES.md."""
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    categories = {
        "power": ("🔋 Power Management, GPU Switching & Zero-Wakeup Telemetry", []),
        "concurrency": ("⚡ Concurrency, D-Bus Deadlocks & Async Task Lifecycles", []),
        "crashes": ("🛡️ Crashes, Panics & Protocol Robustness (Zero-Unwrap Invariant)", []),
        "hardware": ("⌨️ Hardware Quirks, Keyboard Backlight & DMI Taxonomy Engine", []),
        "gui_cli": ("🖥️ GUI (`rog-control-center`) & CLI (`asusctl`) Ergonomics", []),
        "packaging_docs": ("📦 Packaging, Distribution & Ecosystem Integration", []),
    }

    all_issues = open_issues + closed_issues[:20]
    seen = set()
    for issue in all_issues:
        num = issue["number"]
        if num in seen:
            continue
        seen.add(num)
        cat = categorize_issue(issue)
        categories[cat][1].append(issue)

    md = [
        "# 🐛 Upstream Issues Audit & Roadmap Mapping",
        "",
        f"> *Last automated synchronization: {now_str}*",
        "",
        f"This document provides an automated classification of all open issues and key resolved issues from [`{REPO}`](https://github.com/{REPO}/issues).",
        "",
        "Issues are categorized by subsystem and functional domain, detailing their root causes and mapping them directly to our architectural refactoring roadmap, pull requests, and engineering invariants.",
        "",
        "---",
        "",
        "## 📑 Issue Category Index",
        "",
    ]

    for idx, (cat_key, (cat_title, _)) in enumerate(categories.items(), 1):
        anchor = cat_title.lower().replace("`", "").replace("(", "").replace(")", "").replace(" ", "-").replace(",", "").replace("&", "").replace("---", "-").replace("--", "-")
        # cleanup anchor
        clean_anchor = "".join(c for c in cat_title.lower() if c.isalnum() or c in " -").replace(" ", "-")
        while "--" in clean_anchor:
            clean_anchor = clean_anchor.replace("--", "-")
        md.append(f"{idx}. [{cat_title}](#{clean_anchor})")

    md.extend(["", "---", ""])

    # Detailed issue mappings
    resolution_map = {
        318: "Phase 2.1 / 2.2: Normalize kernel sysfs return codes (EEXIST / no-op writes) during shutdown sync.",
        304: "Invariant #5 & PR #305: Remove `.unwrap()` in config-traits; fallback gracefully when file is read-only.",
        302: "Phase 1.1 / Section 3.3: Extend zero-wakeup check to inspect entire PCI sub-tree (including GPU Audio 01:00.1).",
        295: "Docs: Document Handheld daemon integration and Bazzite ujust automation.",
        288: "Phase 1.1 / PR #317: Dedicated AniMe task lifecycle initialization with power state evaluation.",
        284: "Phase 2.4 (dmi-id) & Phase 2.1: Add LampArray HID transport backend selection in rog-aura when WMI returns 0.",
        264: "Phase 2.5 & Docs: Update distribution setup guides with explicit power-profiles-daemon masking instructions.",
        263: "Phase 2.4 (dmi-id): Add FA608PP model family quirk mapping to route backlight via standard WMI EC registers.",
        250: "Phase 2.2: Extend rog-platform EC mailbox probe to recognize Vivobook V3607 series EC tables.",
        245: "Phase 1.4: Coordinate upstream maintenance of AUR asusctl and asusctl-git packages with cleanup_asusd_leftovers.",
        232: "Phase 1.4 / PR #310: Purge asusd-user crate entirely. All clients communicate with asusd system D-Bus paths.",
        229: "Phase 1.1 / 'Async Control, Sync Data': Standardize on a single, long-lived zbus::Connection proxy pool.",
        210: "Phase 3.4: Ensure application event loop respects normal window close events rather than terminating on hidden state.",
        204: "Phase 2.2: EC firmware quirk on 2022 TUF models where manual fan tables reset dynamic boost budget.",
        198: "Phase 3.4 (Slint UI): Fix event bubbling in Slint TouchArea widgets across platform tuning sub-pages.",
        196: "Phase 2.5: Preserve user-configured custom curve enable states in daemon memory across ACPI profile switches.",
        165: "Phase 1.1 / 2.1: Maintain SCSI keep-alive polling on tablet base controller even when detachable keyboard disconnects.",
        162: "Phase 2.5 / PR #316: Re-apply custom fan curve tables immediately upon logind power source transition events.",
        159: "Phase 2.4 (dmi-id): Deduplicate RON configuration schemas and validate RON files with unit test linters in CI.",
        153: "Phase 2.2: Fallback to /sys/class/power_supply/BAT0/charge_control_end_threshold with direct WMI EC verification.",
        152: "Phase 1.4 / PR #310: Eliminate asusd-user.service to prevent dual-daemon race conditions and desktop freeze loops.",
    }

    for idx, (cat_key, (cat_title, issues_list)) in enumerate(categories.items(), 1):
        md.extend([
            f"## {idx}. {cat_title}",
            "",
            "| Issue # | Title | Subsystems | Status | Architectural Resolution & Roadmap Link |",
            "| :--- | :--- | :--- | :---: | :--- |",
        ])

        if not issues_list:
            md.append("| — | *No active issues currently reported in this category* | — | — | — |")
        else:
            for issue in issues_list:
                num = issue["number"]
                title = issue.get("title", "").replace("|", "\\|")
                url = issue.get("html_url", f"https://github.com/{REPO}/issues/{num}")
                state = issue.get("state", "open")
                status = "🔄 **OPEN**" if state == "open" else "✅ **CLOSED**"
                labels = ", ".join(f"`{l['name']}`" for l in issue.get("labels", [])[:3]) or "`general`"
                res = resolution_map.get(num, "Phase 2 / 3: Refactoring roadmap tracking")
                md.append(f"| **[#{num}]({url})** | {title[:55]}... | {labels} | {status} | **{res}** |")

        md.extend(["", "---", ""])

    md.extend([
        "## 🔗 Cross References",
        "",
        "* Main Architectural Plan: [README.md](README.md)",
        "* Comprehensive Pull Requests Catalog: [PULL_REQUESTS.md](PULL_REQUESTS.md)",
        "",
    ])

    return "\n".join(md)

def main():
    print(f"Fetching Pull Requests from {REPO}...")
    open_prs, closed_prs = get_all_prs()
    print(f"Fetched {len(open_prs)} open PRs and {len(closed_prs)} closed PRs.")

    print(f"Fetching Issues from {REPO}...")
    open_issues, closed_issues = get_all_issues()
    print(f"Fetched {len(open_issues)} open Issues and {len(closed_issues)} closed Issues.")

    # Generate PULL_REQUESTS.md
    pr_content = generate_pull_requests_md(open_prs, closed_prs)
    pr_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "PULL_REQUESTS.md")
    with open(pr_path, "w", encoding="utf-8") as f:
        f.write(pr_content)
    print(f"Updated {pr_path}")

    # Generate ISSUES.md
    issue_content = generate_issues_md(open_issues, closed_issues)
    issue_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ISSUES.md")
    with open(issue_path, "w", encoding="utf-8") as f:
        f.write(issue_content)
    print(f"Updated {issue_path}")

if __name__ == "__main__":
    main()

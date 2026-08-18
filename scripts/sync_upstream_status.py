#!/usr/bin/env python3
"""
Sync Upstream Status Script for asusctl-refactoring.

Fetches open PRs and Issues from OpenGamingCollective/asusctl,
synchronizes and updates diagnostic mappings in roadmap_mapping.json,
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
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MAPPING_FILE = os.path.join(SCRIPT_DIR, "roadmap_mapping.json")

def load_roadmap_mapping() -> tuple[dict, dict]:
    """Load curated PR and Issue diagnostic metadata from JSON."""
    if not os.path.exists(MAPPING_FILE):
        return {}, {}
    try:
        with open(MAPPING_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("pull_requests", {}), data.get("issues", {})
    except Exception as e:
        print(f"Warning: Failed to load {MAPPING_FILE}: {e}", file=sys.stderr)
        return {}, {}

def save_roadmap_mapping(pr_mappings: dict, issue_mappings: dict) -> bool:
    """Save updated PR and Issue diagnostic metadata to JSON."""
    payload = {
        "pull_requests": dict(sorted(pr_mappings.items(), key=lambda x: int(x[0]), reverse=True)),
        "issues": dict(sorted(issue_mappings.items(), key=lambda x: int(x[0]), reverse=True)),
    }
    try:
        with open(MAPPING_FILE, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
            f.write("\n")
        return True
    except Exception as e:
        print(f"Error saving {MAPPING_FILE}: {e}", file=sys.stderr)
        return False

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
    """Fetch open issues only (excluding PRs)."""
    open_issues = fetch_github_api("issues", {"state": "open", "per_page": 100})
    # Filter out pull requests which GitHub API includes in /issues
    return [i for i in open_issues if "pull_request" not in i]

def sync_and_prune_mappings(open_prs: list, open_issues: list, pr_mappings: dict, issue_mappings: dict) -> bool:
    """Auto-discover new PRs/Issues and prune stale closed issues from mapping file."""
    changed = False

    # 1. Register new open PRs if not already present
    for pr in open_prs:
        num_str = str(pr["number"])
        if num_str not in pr_mappings:
            pr_mappings[num_str] = {
                "action": "Evaluate for roadmap integration",
                "phase": "Phase 2 / 3",
                "reopen_candidate": False,
            }
            print(f"Auto-registered new PR #{num_str} in roadmap mapping.")
            changed = True

    # 2. Register new open Issues if not already present
    open_issue_nums = {str(i["number"]) for i in open_issues}
    for issue in open_issues:
        num_str = str(issue["number"])
        if num_str not in issue_mappings:
            labels = [l["name"].lower() for l in issue.get("labels", [])]
            title = issue.get("title", "").lower()
            is_bug = "bug" in labels or "bug" in title or "panic" in title or "crash" in title
            status = "⚠️ **ACTIVE BUG**" if is_bug else "💡 **FEATURE REQUEST**"
            issue_mappings[num_str] = {
                "status": status,
                "resolution": "Phase 2 / 3: Upstream issue triage & investigation",
            }
            print(f"Auto-registered new Issue #{num_str} ({status}) in roadmap mapping.")
            changed = True

    # 3. Prune closed issues from mapping (keep only currently open issues)
    stale_issue_keys = [k for k in issue_mappings.keys() if k not in open_issue_nums]
    if stale_issue_keys:
        for k in stale_issue_keys:
            del issue_mappings[k]
            print(f"Pruned closed/resolved Issue #{k} from roadmap mapping.")
        changed = True

    return changed

def assess_pr(pr: dict, pr_mappings: dict) -> tuple[str, str, str]:
    """Return status icon, recommended action, and roadmap phase for PR."""
    num_str = str(pr["number"])
    is_merged = pr.get("merged_at") is not None
    state = pr.get("state", "open")

    if num_str in pr_mappings:
        entry = pr_mappings[num_str]
        action = entry.get("action", "Evaluate for roadmap integration")
        phase = entry.get("phase", "Phase 2 / 3")
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

def generate_pull_requests_md(open_prs: list, closed_prs: list, pr_mappings: dict) -> str:
    """Generate markdown content for PULL_REQUESTS.md focusing on active and actionable PRs."""
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    # Keep active open PRs + specifically actionable closed PRs flagged in mapping
    reopen_ids = {int(k) for k, v in pr_mappings.items() if v.get("reopen_candidate")}
    reopen_prs = [p for p in closed_prs if p["number"] in reopen_ids]
    all_prs = open_prs + reopen_prs

    # Deduplicate by number
    seen = set()
    unique_prs = []
    for pr in all_prs:
        if pr["number"] not in seen:
            seen.add(pr["number"])
            unique_prs.append(pr)

    unique_prs.sort(key=lambda p: p["number"], reverse=True)

    md = [
        "# 🔀 Active Pull Request Catalog & Architectural Assessment",
        "",
        f"> *Last automated synchronization: {now_str}*",
        "",
        f"This document provides an automated audit of active and actionable upstream pull requests from [`{REPO}`](https://github.com/{REPO}/pulls).",
        "",
        "Each pull request is evaluated for its architectural impact, alignment with the **\"Async Control, Sync Data\"** paradigm, dependency health, and whether it should be merged, kept, or reopened.",
        "",
        "---",
        "",
        "## 📑 Summary Matrix (Active & Actionable PRs)",
        "",
        "| PR # | Type / Area | Branch / Scope | Status | Recommended Action | Roadmap Phase |",
        "| :--- | :--- | :--- | :---: | :--- | :---: |",
    ]

    for pr in unique_prs:
        num = pr["number"]
        title = pr.get("title", "").replace("|", "\\|")
        branch = pr.get("head", {}).get("ref", "unknown")
        url = pr.get("html_url", f"https://github.com/{REPO}/pull/{num}")
        status, action, phase = assess_pr(pr, pr_mappings)
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

def generate_issues_md(open_issues: list, issue_mappings: dict) -> str:
    """Generate markdown content for ISSUES.md containing only open issues."""
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    categories = {
        "power": ("🔋 Power Management, GPU Switching & Zero-Wakeup Telemetry", []),
        "concurrency": ("⚡ Concurrency, D-Bus Deadlocks & Async Task Lifecycles", []),
        "crashes": ("🛡️ Crashes, Panics & Protocol Robustness (Zero-Unwrap Invariant)", []),
        "hardware": ("⌨️ Hardware Quirks, Keyboard Backlight & DMI Taxonomy Engine", []),
        "gui_cli": ("🖥️ GUI (`rog-control-center`) & CLI (`asusctl`) Ergonomics", []),
        "packaging_docs": ("📦 Packaging, Distribution & Ecosystem Integration", []),
    }

    seen = set()
    for issue in open_issues:
        num = issue["number"]
        if num in seen:
            continue
        seen.add(num)
        cat = categorize_issue(issue)
        categories[cat][1].append(issue)

    md = [
        "# 🐛 Active Upstream Issues & Roadmap Mapping",
        "",
        f"> *Last automated synchronization: {now_str}*",
        "",
        f"This document provides an automated classification of all **active open issues** from [`{REPO}`](https://github.com/{REPO}/issues).",
        "",
        "Issues are categorized by subsystem and functional domain, detailing their root causes and mapping them directly to our architectural refactoring roadmap, pull requests, and engineering invariants.",
        "",
        "---",
        "",
        "## 📑 Issue Category Index",
        "",
    ]

    for idx, (cat_key, (cat_title, _)) in enumerate(categories.items(), 1):
        clean_anchor = "".join(c for c in cat_title.lower() if c.isalnum() or c in " -").replace(" ", "-")
        while "--" in clean_anchor:
            clean_anchor = clean_anchor.replace("--", "-")
        md.append(f"{idx}. [{cat_title}](#{clean_anchor})")

    md.extend(["", "---", ""])

    for idx, (cat_key, (cat_title, issues_list)) in enumerate(categories.items(), 1):
        md.extend([
            f"## {idx}. {cat_title}",
            "",
            "| Issue # | Title | Subsystems | Status / Fix Verification | Architectural Resolution & Roadmap Link |",
            "| :--- | :--- | :--- | :---: | :--- |",
        ])

        if not issues_list:
            md.append("| — | *No active open issues currently reported in this category* | — | — | — |")
        else:
            for issue in issues_list:
                num = issue["number"]
                num_str = str(num)
                title = issue.get("title", "").replace("|", "\\|")
                url = issue.get("html_url", f"https://github.com/{REPO}/issues/{num}")
                labels = ", ".join(f"`{l['name']}`" for l in issue.get("labels", [])[:3]) or "`general`"

                if num_str in issue_mappings:
                    diag_status = issue_mappings[num_str].get("status", "⚠️ **ACTIVE BUG**")
                    res = issue_mappings[num_str].get("resolution", "Phase 2 / 3: Refactoring roadmap tracking")
                else:
                    diag_status = "⚠️ **ACTIVE BUG**" if "bug" in labels else "💡 **FEATURE REQUEST**"
                    res = "Phase 2 / 3: Refactoring roadmap tracking"

                md.append(f"| **[#{num}]({url})** | {title[:55]}... | {labels} | {diag_status} | **{res}** |")

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
    # 1. Load curated roadmap mappings
    pr_mappings, issue_mappings = load_roadmap_mapping()
    print(f"Loaded {len(pr_mappings)} PR mappings and {len(issue_mappings)} Issue mappings from {MAPPING_FILE}")

    # 2. Fetch live data from GitHub
    print(f"Fetching Pull Requests from {REPO}...")
    open_prs, closed_prs = get_all_prs()
    print(f"Fetched {len(open_prs)} open PRs and {len(closed_prs)} closed PRs.")

    print(f"Fetching Open Issues from {REPO}...")
    open_issues = get_all_issues()
    print(f"Fetched {len(open_issues)} open Issues.")

    # 3. Synchronize and auto-update mapping dictionary (add new, prune closed)
    mapping_changed = sync_and_prune_mappings(open_prs, open_issues, pr_mappings, issue_mappings)
    if mapping_changed:
        save_roadmap_mapping(pr_mappings, issue_mappings)
        print(f"Successfully synchronized and saved updated {MAPPING_FILE}")

    # 4. Generate PULL_REQUESTS.md
    pr_content = generate_pull_requests_md(open_prs, closed_prs, pr_mappings)
    pr_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "PULL_REQUESTS.md")
    with open(pr_path, "w", encoding="utf-8") as f:
        f.write(pr_content)
    print(f"Updated {pr_path}")

    # 5. Generate ISSUES.md
    issue_content = generate_issues_md(open_issues, issue_mappings)
    issue_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ISSUES.md")
    with open(issue_path, "w", encoding="utf-8") as f:
        f.write(issue_content)
    print(f"Updated {issue_path}")

if __name__ == "__main__":
    main()

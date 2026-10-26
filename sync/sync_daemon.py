#!/usr/bin/env python3
"""
Antigravity Conversation & InfinityFree Manager GitHub Auto-Sync Daemon
Tracks conversation transcripts, artifacts, domain catalogs, and codebase changes,
then automatically formats, commits, and pushes them to GitHub.
"""

import os
import sys
import time
import json
import shutil
import subprocess
import argparse
from datetime import datetime
from pathlib import Path

CONVERSATION_ID = "ce8d996e-7ead-45d9-aaae-b8c03cf0515a"
BRAIN_DIR = Path(f"/home/alpesh/.gemini/antigravity/brain/{CONVERSATION_ID}")
REPO_DIR = Path(__file__).resolve().parent.parent
CONVERSATION_DIR = REPO_DIR / "conversation"
ARTIFACTS_DIR = REPO_DIR / "artifacts"


def parse_transcript_to_markdown(jsonl_path: Path) -> str:
    """Parses raw JSONL transcript into a structured, readable Markdown log."""
    if not jsonl_path.exists():
        return "# Conversation Log\n\n*No transcript available yet.*"

    md_lines = [
        "# 🤖 Antigravity Conversation Session Log",
        f"**Conversation ID**: `{CONVERSATION_ID}`  ",
        f"**Last Synced**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  ",
        "",
        "---",
        ""
    ]

    try:
        with open(jsonl_path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue

                step_type = entry.get("type", "")
                created_at = entry.get("created_at", "")
                content = entry.get("content", "")
                thinking = entry.get("thinking", "")
                tool_calls = entry.get("tool_calls", [])

                if step_type == "USER_INPUT":
                    md_lines.append(f"### 👤 User Request ({created_at})\n")
                    md_lines.append(f"{content.strip()}\n")
                    md_lines.append("\n---\n")

                elif step_type == "PLANNER_RESPONSE":
                    md_lines.append(f"### 🤖 Antigravity Agent Response ({created_at})\n")
                    if thinking:
                        md_lines.append(f"<details><summary>🧠 Agent Internal Thought Process</summary>\n\n```text\n{thinking.strip()}\n```\n</details>\n")
                    if tool_calls:
                        md_lines.append("**Executed Tools:**")
                        for tc in tool_calls:
                            func = tc.get("function", {})
                            name = func.get("name", "tool")
                            args = func.get("arguments", {})
                            summary = args.get("toolSummary", name) if isinstance(args, dict) else name
                            md_lines.append(f"- 🔧 `{name}`: {summary}")
                        md_lines.append("")
                    if content and content.strip():
                        md_lines.append(f"{content.strip()}\n")
                    md_lines.append("\n---\n")

                elif step_type == "TOOL_OUTPUT":
                    output = entry.get("output", "")
                    if output:
                        snippet = output[:300] + ("..." if len(output) > 300 else "")
                        md_lines.append(f"<details><summary>📄 Tool Output Preview</summary>\n\n```text\n{snippet}\n```\n</details>\n")
    except Exception as e:
        md_lines.append(f"\n*Error formatting transcript: {e}*\n")

    return "\n".join(md_lines)


def update_catalog_markdown():
    """Regenerates DOMAINS.md from current catalog."""
    try:
        sys.path.insert(0, str(REPO_DIR))
        from agent.catalog import DomainCatalog
        from agent.markdown_generator import MarkdownGenerator
        catalog = DomainCatalog(REPO_DIR / "config" / "domains.json")
        MarkdownGenerator.write_domains_md(catalog.list_all())
    except Exception as e:
        print(f"Notice: Could not regenerate DOMAINS.md: {e}")


def sync_cycle() -> bool:
    """Executes a single synchronization cycle. Returns True if changes were pushed."""
    CONVERSATION_DIR.mkdir(parents=True, exist_ok=True)
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Sync Transcripts
    logs_dir = BRAIN_DIR / ".system_generated" / "logs"
    transcript_src = logs_dir / "transcript.jsonl"
    transcript_full_src = logs_dir / "transcript_full.jsonl"

    if transcript_src.exists():
        shutil.copy2(transcript_src, CONVERSATION_DIR / "transcript.jsonl")
        formatted_md = parse_transcript_to_markdown(transcript_src)
        with open(CONVERSATION_DIR / "CONVERSATION.md", "w", encoding="utf-8") as f:
            f.write(formatted_md)

    if transcript_full_src.exists():
        shutil.copy2(transcript_full_src, CONVERSATION_DIR / "transcript_full.jsonl")

    # 2. Sync Artifacts (implementation_plan.md, walkthrough.md, etc.)
    if BRAIN_DIR.exists():
        for item in BRAIN_DIR.glob("*.md"):
            shutil.copy2(item, ARTIFACTS_DIR / item.name)

    # 3. Update DOMAINS.md
    update_catalog_markdown()

    # 4. Check Git Status
    subprocess.run(["git", "add", "."], cwd=REPO_DIR, capture_output=True)
    status = subprocess.run(
        ["git", "status", "--porcelain"], cwd=REPO_DIR, capture_output=True, text=True
    )

    if not status.stdout.strip():
        return False

    # 5. Commit and Push
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    commit_msg = f"🤖 Auto-Sync: Antigravity Conversation & InfinityFree Agent [{now_str}]"

    subprocess.run(["git", "commit", "-m", commit_msg], cwd=REPO_DIR, capture_output=True)
    push_res = subprocess.run(["git", "push", "origin", "main"], cwd=REPO_DIR, capture_output=True, text=True)

    if push_res.returncode == 0:
        print(f"[{now_str}] Successfully synced conversation & code to GitHub main!")
        return True
    else:
        print(f"[{now_str}] Push output: {push_res.stderr.strip() or push_res.stdout.strip()}")
        return False


def main():
    parser = argparse.ArgumentParser(description="InfinityFree Agent & Antigravity to GitHub Auto-Sync")
    parser.add_argument("--once", action="store_true", help="Run sync once and exit")
    parser.add_argument("--interval", type=int, default=20, help="Sync interval in seconds (default: 20)")
    args = parser.parse_args()

    if args.once:
        synced = sync_cycle()
        print("One-shot sync complete." if synced else "No changes to sync.")
        return

    print(f"Starting InfinityFree Agent continuous sync daemon (interval: {args.interval}s)...")
    while True:
        try:
            sync_cycle()
        except Exception as e:
            print(f"Sync error: {e}")
        time.sleep(args.interval)


if __name__ == "__main__":
    main()

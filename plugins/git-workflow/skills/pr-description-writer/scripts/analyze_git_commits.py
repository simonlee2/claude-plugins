#!/usr/bin/env python3
"""
Analyze git commits for the current branch and generate structured PR information.
This script helps generate or update PR descriptions by analyzing commit history and changes.
"""

import subprocess
import json
import sys
from pathlib import Path


def get_current_branch():
    """Get the current git branch name."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        print("Error: Not in a git repository", file=sys.stderr)
        sys.exit(1)


def get_main_branch():
    """Detect the main branch (main or master)."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--verify", "main"],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            return "main"
    except:
        pass

    try:
        result = subprocess.run(
            ["git", "rev-parse", "--verify", "master"],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            return "master"
    except:
        pass

    return "main"  # Default assumption


def get_commits_for_branch(base_branch="main"):
    """Get all commits on current branch not in base branch."""
    try:
        result = subprocess.run(
            ["git", "log", f"{base_branch}..HEAD", "--pretty=format:%H|%s|%b|%an"],
            capture_output=True,
            text=True,
            check=True,
        )
        commits = []
        for line in result.stdout.strip().split("\n"):
            if line:
                parts = line.split("|", 3)
                commits.append(
                    {
                        "hash": parts[0],
                        "subject": parts[1],
                        "body": parts[2] if len(parts) > 2 else "",
                        "author": parts[3] if len(parts) > 3 else "",
                    }
                )
        return commits
    except subprocess.CalledProcessError as e:
        print(f"Error getting commits: {e}", file=sys.stderr)
        return []


def get_file_changes(base_branch="main"):
    """Get summary of file changes: added, modified, deleted."""
    try:
        result = subprocess.run(
            ["git", "diff", f"{base_branch}...HEAD", "--name-status"],
            capture_output=True,
            text=True,
            check=True,
        )

        added = []
        modified = []
        deleted = []

        for line in result.stdout.strip().split("\n"):
            if not line:
                continue
            parts = line.split("\t")
            status = parts[0]
            filepath = parts[1] if len(parts) > 1 else ""

            if status == "A":
                added.append(filepath)
            elif status == "M":
                modified.append(filepath)
            elif status == "D":
                deleted.append(filepath)

        return {"added": added, "modified": modified, "deleted": deleted}
    except subprocess.CalledProcessError as e:
        print(f"Error getting file changes: {e}", file=sys.stderr)
        return {"added": [], "modified": [], "deleted": []}


def get_diff_stats(base_branch="main"):
    """Get statistics about the diff."""
    try:
        result = subprocess.run(
            ["git", "diff", f"{base_branch}...HEAD", "--stat"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error getting diff stats: {e}", file=sys.stderr)
        return ""


def get_short_diff(base_branch="main", max_lines=500):
    """Get a short summary of the actual changes."""
    try:
        result = subprocess.run(
            ["git", "diff", f"{base_branch}...HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        lines = result.stdout.split("\n")
        # Return first max_lines to keep output reasonable
        return "\n".join(lines[:max_lines])
    except subprocess.CalledProcessError as e:
        print(f"Error getting diff: {e}", file=sys.stderr)
        return ""


def analyze_pr_info():
    """Main function to analyze PR information."""
    current_branch = get_current_branch()
    main_branch = get_main_branch()

    print(f"Current branch: {current_branch}")
    print(f"Base branch: {main_branch}\n")

    commits = get_commits_for_branch(main_branch)
    file_changes = get_file_changes(main_branch)
    diff_stats = get_diff_stats(main_branch)

    print("=== COMMITS ===")
    for i, commit in enumerate(commits, 1):
        print(f"\n{i}. {commit['subject']}")
        if commit["body"]:
            print(f"   {commit['body'][:200]}...")

    print("\n\n=== FILE CHANGES ===")
    print(f"Added ({len(file_changes['added'])} files):")
    for f in file_changes["added"][:10]:
        print(f"  + {f}")
    if len(file_changes["added"]) > 10:
        print(f"  ... and {len(file_changes['added']) - 10} more")

    print(f"\nModified ({len(file_changes['modified'])} files):")
    for f in file_changes["modified"][:10]:
        print(f"  M {f}")
    if len(file_changes["modified"]) > 10:
        print(f"  ... and {len(file_changes['modified']) - 10} more")

    if file_changes["deleted"]:
        print(f"\nDeleted ({len(file_changes['deleted'])} files):")
        for f in file_changes["deleted"][:10]:
            print(f"  - {f}")
        if len(file_changes["deleted"]) > 10:
            print(f"  ... and {len(file_changes['deleted']) - 10} more")

    print("\n\n=== DIFF STATS ===")
    print(diff_stats)

    # Output structured data as JSON for programmatic use
    data = {
        "current_branch": current_branch,
        "base_branch": main_branch,
        "commits": commits,
        "file_changes": file_changes,
        "stats": {
            "total_commits": len(commits),
            "files_added": len(file_changes["added"]),
            "files_modified": len(file_changes["modified"]),
            "files_deleted": len(file_changes["deleted"]),
        },
    }

    return data


if __name__ == "__main__":
    analyze_pr_info()

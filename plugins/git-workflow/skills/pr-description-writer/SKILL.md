---
name: pr-description-writer
description: This skill generates and improves GitHub pull request descriptions that help reviewers understand context and promote effective code reviews. Use this skill when creating new PRs, updating PR descriptions with new commits, or reviewing existing PR descriptions for quality. The skill analyzes git commits to extract key changes and generates descriptions with proper context (why), implementation details (how), file prioritization for large PRs, and testing strategy.
---

# PR Description Writer

## Overview

This skill generates comprehensive, reviewer-friendly pull request descriptions by analyzing git commits and changes. It helps authors communicate their changes effectively, enabling reviewers to understand context, give better feedback, and spend less time orienting themselves to the code.

The skill handles three main scenarios:
1. **Generate a new PR description** from scratch based on commits since the main branch
2. **Update an existing PR description** when new commits are added to an in-flight PR
3. **Review and improve an existing PR description** for quality and completeness

## When to Use This Skill

- **Creating a new PR**: You've made commits on a feature branch and need a description to open a PR
- **PR in review with new commits**: You've added commits to address feedback; the description needs updating
- **Reviewing a PR description**: You want to ensure a PR description meets quality standards and helps reviewers

## How to Use This Skill

### Scenario 1: Generate a New PR Description

**User request:** "Write a PR description for my changes"

**What Claude will do:**
1. Run `scripts/analyze_git_commits.py` to analyze commits and file changes
2. Extract key information about what was changed and why (from commit messages)
3. Identify files that need special attention (core logic vs. supporting changes)
4. Generate a comprehensive PR description following the structured template
5. Reference `references/pr_description_guide.md` for best practices

**What to expect:**
- A complete PR description with Summary, Context, Implementation, File organization, Testing strategy, and Risk assessment
- Clear guidance on what files to review first
- Specific testing instructions reviewers can follow
- Explicit risk flags (breaking changes, performance impacts, etc.)

### Scenario 2: Update Existing PR with New Commits

**User request:** "Update the PR description to reflect the new commits I just added"

**What Claude will do:**
1. Analyze the new commits since the last PR description was written
2. Read the existing PR description to understand the original intent
3. Determine what sections need updating (usually Implementation and Testing)
4. Update the description while preserving the overall structure and context
5. Ensure file lists and risk assessment are current

**What to expect:**
- An updated PR description that acknowledges the new changes
- Maintains continuity with the original context and purpose
- Clearly shows what changed since the last description
- Ready to paste back into GitHub

### Scenario 3: Review and Improve a PR Description

**User request:** "Review this PR description for quality" or "Improve this PR description"

**What Claude will do:**
1. Analyze the existing PR description against best practices in `references/pr_description_guide.md`
2. Identify gaps (missing context, unclear implementation, insufficient testing details)
3. Generate an improved version or provide specific feedback on what's missing
4. Suggest additions based on the actual git changes

**What to expect:**
- Comprehensive feedback on what's weak and why
- A revised description incorporating all best practices
- Suggestions for testing strategy or risk assessment if missing
- Comparison to best practices with examples

## Key Principles

**1. Follow the commits, don't invent**
The PR description is derived from what's actually in the git commits. Commit messages are the source of truth for what was changed and why.

**2. Organize by importance, not just by file list**
For large PRs, explicitly call out which files contain critical logic that must be reviewed first. Distinguish core changes from supporting changes (tests, docs, configuration).

**3. Explain the "why" before the "what"**
Context about business needs, design decisions, and tradeoffs is more important than a file-by-file breakdown of changes.

**4. Provide actionable testing guidance**
Reviewers should be able to validate the changes by following the testing instructions without hunting for information.

## Resources

### scripts/analyze_git_commits.py
Python script that analyzes git commits and changes to extract structured information:
- Lists all commits on the current branch not in main/master
- Shows which files were added, modified, or deleted
- Provides diff statistics
- Outputs both human-readable summary and structured data

Run this script to gather input for PR descriptions.

### references/pr_description_guide.md
Comprehensive guide documenting:
- Core principles of effective PR descriptions
- Recommended section structure (Summary, Context, Implementation, Review Priority, Testing, Risk Assessment)
- Best practices for PRs of different sizes
- Common anti-patterns to avoid
- Special guidance for large PRs with file prioritization
- Examples of good vs. weak PR descriptions (see assets/)
- Impact of good descriptions on code review quality

This is the authoritative reference for PR description best practices.

### assets/
Example PR descriptions showing best practices:
- `pr_template.md` – Basic template structure
- `example_good_pr.md` – Comprehensive example of a well-written PR description with all sections properly filled
- `example_weak_pr.md` – Example of weak description before improvement, with annotations on what's wrong and how to fix it

Use these examples to understand the expected level of detail and structure.

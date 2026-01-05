---
description: Create a git commit and push to the remote repository without creating a PR
---

# Commit and Push

Create a git commit and push to the remote repository without creating a PR.

Follow these steps:

1. Run `git status`, `git diff`, and `git log` in parallel to understand:
   - Current untracked/modified files
   - Changes that will be committed (both staged and unstaged)
   - Recent commit message style

2. Analyze the changes and draft a concise commit message that:
   - Summarizes the nature of changes (new feature, enhancement, bug fix, refactoring, etc.)
   - Focuses on "why" rather than "what"
   - Follows the repository's commit message style
   - Is 1-2 sentences maximum

3. Add relevant files, create the commit, and push:
   - Add untracked/modified files that are relevant to the changes
   - Do NOT commit files that likely contain secrets (.env, credentials.json, etc)
   - Create the commit using a HEREDOC format for the message
   - Push to the remote repository
   - Run `git status` after to verify success

4. If the commit fails due to pre-commit hooks modifying files:
   - Check if it's safe to amend (check authorship and that commit wasn't pushed)
   - If safe, amend the commit
   - Otherwise, create a new commit

IMPORTANT:
- NEVER update git config
- NEVER run destructive git commands unless explicitly requested
- NEVER skip hooks (--no-verify, --no-gpg-sign)
- NEVER force push to main/master
- Warn if files contain potential secrets
- Only commit when explicitly asked (via this command)

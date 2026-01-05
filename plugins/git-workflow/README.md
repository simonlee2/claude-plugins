# git-workflow

Git workflow automation plugin for Claude Code with smart commits and PR description generation.

## Features

### Command: `/git-workflow:commit-push`

Automatically create commits and push to remote without creating a PR.

**What it does:**
- Analyzes your git changes (status, diff, log)
- Generates smart commit messages following repository conventions
- Handles pre-commit hooks gracefully
- Pushes to remote automatically

**Usage:**
```
/git-workflow:commit-push
```

Claude will:
1. Review your changes
2. Draft a concise commit message focusing on "why" not "what"
3. Add relevant files
4. Create the commit
5. Push to remote
6. Verify success

**Best practices enforced:**
- Follows repository commit message style
- Warns about files that may contain secrets
- Never skips git hooks
- Never force pushes to main/master
- Handles pre-commit hook file modifications

### Skill: pr-description-writer

Automatically activates when you need to create or improve PR descriptions.

**Capabilities:**
- Generates comprehensive PR descriptions from git commits
- Analyzes commit history to extract key changes
- Provides proper context (why), implementation details (how)
- Prioritizes files for large PRs
- Includes testing strategy
- Updates existing PR descriptions with new commits

**When it activates:**
- "Write a PR description for my changes"
- "Generate a PR description"
- "Update the PR description"
- "Improve this PR description"

**What you get:**
- Summary of changes
- Context explaining business needs
- Implementation details
- File prioritization for reviewers
- Testing strategy
- Risk assessment

## Installation

### From marketplace (once published):
```bash
/plugin marketplace add simon-username/claude-plugins
/plugin install git-workflow@simon-plugins
```

### Local testing:
```bash
/plugin marketplace add ~/Developer/claude-plugins
/plugin install git-workflow@simon-plugins
```

## Requirements

- Git installed and configured
- Repository with remote configured
- Appropriate git credentials set up

## Configuration

No configuration required. The plugin adapts to your repository's existing commit message style.

## Examples

### Quick commit and push
```
User: "Commit and push my changes"
Claude: [Activates /git-workflow:commit-push]
        Analyzes changes...
        Creates commit: "Add user authentication with JWT tokens"
        Pushes to origin/feature-branch
```

### Generate PR description
```
User: "Write a PR description for my feature branch"
Claude: [Activates pr-description-writer skill]
        Analyzes commits...
        Generates comprehensive PR description with:
        - Summary
        - Context and motivation
        - Implementation approach
        - Files to review first
        - Testing instructions
        - Risk assessment
```

## Components

- `commands/commit-push.md` - Command for commit and push workflow
- `skills/pr-description-writer/` - Skill for PR description generation
  - `SKILL.md` - Skill definition and usage
  - `scripts/analyze_git_commits.py` - Commit analysis tool
  - `references/pr_description_guide.md` - Best practices guide
  - `assets/` - Example PR descriptions

## Contributing

This is a personal plugin collection. Feel free to fork and adapt for your needs.

## License

MIT License - see LICENSE file for details

## Support

For issues or questions, open an issue in the repository.

---
name: create-cli
description: This skill should be used when the user asks to "design a CLI", "create command-line interface", "design CLI parameters", "plan CLI UX", or needs help structuring command-line tool interfaces with proper arguments, flags, subcommands, and user experience patterns.
---

# CLI Design Skill

## Overview

This skill guides the design of command-line interface specifications before implementation or during refactoring. It focuses on creating CLIs that are both human-friendly and script-compatible, following established best practices and conventions.

## When to Use This Skill

Use this skill when:
- Designing a new command-line tool from scratch
- Refactoring an existing CLI to improve UX
- Planning CLI parameters, flags, and subcommands
- Defining help text, error messages, and output formats
- Establishing configuration precedence and environment handling
- Designing safe operation modes (dry-run, confirmations, force flags)

## Design Workflow

### Step 1: Clarification

Ask minimal questions to understand the CLI's purpose:

**Command Purpose:**
- What does this command do?
- Who will use it? (humans, automation scripts, or both)
- Is this a single command or a suite with subcommands?

**Input Contract:**
- How does input flow in? (command arguments, stdin, files, interactive prompts)
- What parameters are required vs optional?
- Should it support batch/bulk operations?

**Output Contract:**
- What format should output use? (human-readable text, JSON, structured data)
- What goes to stdout vs stderr?
- Should it support multiple output formats?

**Interactivity:**
- Are interactive prompts appropriate?
- Should there be a non-interactive mode?
- How should it behave when piped or in CI environments?

**Configuration:**
- What's configurable? (flags, environment variables, config files)
- What's the precedence order?
- Are defaults sensible?

### Step 2: Deliverable Specification

Produce a compact, implementable spec that includes:

#### 1. Command Tree & Usage

```
USAGE:
  mycli [global-flags] <command> [command-flags] [arguments]

COMMANDS:
  init      Initialize a new project
  build     Build the project
  deploy    Deploy to production

GLOBAL FLAGS:
  -h, --help       Show help
  --version        Show version
  -v, --verbose    Enable verbose output
  --no-color       Disable colored output
```

#### 2. Arguments & Flags Table

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `--config` | path | No | `.config` | Config file path |
| `--output` | path | No | `stdout` | Output destination |
| `--format` | enum | No | `text` | Output format (text, json) |
| `--force` | bool | No | `false` | Skip confirmations |

#### 3. Subcommand Details

For each subcommand, specify:
- Purpose and behavior
- Required/optional arguments
- Flags specific to that subcommand
- State changes or side effects
- Exit codes

#### 4. Output Rules

**stdout:**
- Primary command output
- Machine-parseable data when `--format=json`
- Human-readable results by default

**stderr:**
- Error messages
- Warnings
- Progress indicators (when appropriate)
- Diagnostic information with `--verbose`

#### 5. Exit Codes

```
0   Success
1   General error
2   Invalid usage (missing args, unknown flags)
3   Configuration error
4   Runtime error (operation failed)
130 Interrupted (Ctrl+C)
```

#### 6. Safety Mechanisms

**Dry-run mode:**
```bash
mycli deploy --dry-run    # Show what would happen without doing it
```

**Interactive confirmations:**
```bash
mycli delete database
# Prompt: "Are you sure you want to delete 'database'? [y/N]"
```

**Force flag for non-interactive:**
```bash
mycli delete database --force    # Skip confirmation
```

#### 7. Configuration Precedence

Order of precedence (highest to lowest):
1. Command-line flags
2. Environment variables
3. Config file settings
4. Built-in defaults

Example:
```bash
# Flag overrides env var
MY_CLI_OUTPUT=json mycli --output=text    # Uses text

# Env var overrides config file
export MY_CLI_CONFIG=/custom/config
mycli    # Uses /custom/config instead of .config
```

#### 8. Usage Examples

Provide 5-10 practical examples:

```bash
# Basic usage
mycli build

# With output format
mycli build --format=json > output.json

# Dry-run before executing
mycli deploy --dry-run
mycli deploy --force

# Using environment variables
MY_CLI_VERBOSE=1 mycli build

# Interactive vs non-interactive
mycli delete --force    # Non-interactive
mycli delete           # Prompts for confirmation

# Piping and composition
mycli list --format=json | jq '.[] | select(.status=="active")'
```

## Default Conventions

Unless specified otherwise, apply these defaults:

### Standard Flags

- `-h, --help` - Show help and exit
- `--version` - Show version and exit
- `-v, --verbose` - Enable verbose/debug output
- `--no-color` - Disable colored output (respect `NO_COLOR` env var)
- `--quiet, -q` - Suppress non-essential output
- `--force, -f` - Skip confirmations (for automation)
- `--dry-run` - Simulate operation without making changes

### Terminal Behavior

- Respect `NO_COLOR` environment variable
- Detect `TERM=dumb` and disable colors
- Detect TTY vs pipe and adjust output accordingly
- Use colored output by default when connected to TTY
- Use plain text when output is piped

### Interactive Prompts

- Only prompt when connected to a TTY
- Provide `--no-input` or `--force` for non-interactive mode
- Default to safe choice (e.g., "N" for destructive operations)
- Exit with error code if prompt needed but in non-interactive mode

### Destructive Operations

- Always require confirmation when interactive
- Provide `--force` flag for automation
- Use `--dry-run` to preview impact
- Clear, explicit warnings about consequences
- Consider undo/rollback mechanisms

### Error Handling

- Write errors to stderr, not stdout
- Use specific exit codes for different error types
- Provide actionable error messages
- Suggest fixes when possible
- Include context (what failed, why, how to fix)

## Reference Guidelines

This skill follows the established CLI best practices from:
- **https://clig.dev/** - Command Line Interface Guidelines

Key principles:
- **Human-first design** - Optimize for clarity and discoverability
- **Composability** - Work well with pipes and other tools
- **Consistency** - Follow POSIX conventions where appropriate
- **Robustness** - Handle errors gracefully
- **Accessibility** - Support different terminal capabilities

## Additional Resources

For comprehensive CLI design patterns and best practices, consult `references/cli-guidelines.md`.

## Implementation Notes

- This skill is language-agnostic unless you request specific parsing library recommendations
- Focus on interface design before writing implementation code
- Keep specifications compact and implementable
- Iterate on design based on user feedback
- Consider both human users and automation scripts
- Test CLI behavior in different environments (TTY, pipes, CI)

## Common CLI Patterns

### Progress Indicators

```bash
# Simple spinner for long operations
mycli process --verbose
⠋ Processing files... (15/100)

# Progress bar
[=========>          ] 45% (450/1000 files)

# Suppress with --quiet
mycli process --quiet    # No progress output
```

### Table Output

```bash
# Human-readable table
ID    NAME           STATUS    UPDATED
1     project-a      active    2h ago
2     project-b      paused    1d ago

# JSON for scripts
mycli list --format=json
[{"id":1,"name":"project-a","status":"active"}]
```

### Colored Output

```bash
# Colors when TTY
✓ Success message (green)
⚠ Warning message (yellow)
✗ Error message (red)

# Plain text when piped or NO_COLOR=1
+ Success message
! Warning message
x Error message
```

## Best Practices

1. **Start simple** - Add complexity only when needed
2. **Document thoroughly** - Good help text is essential
3. **Test edge cases** - Empty input, large input, concurrent usage
4. **Provide examples** - Show common use cases in help
5. **Consider accessibility** - Screen readers, different terminals
6. **Plan for evolution** - Design for future extensions
7. **Fail fast** - Validate input early
8. **Be predictable** - Follow conventions and user expectations

## Example Design Session

**User:** "I need to design a CLI for deploying applications to different environments"

**Response:**
"Let me help design that deployment CLI. A few clarifying questions:

1. **Environments**: What environments will you deploy to? (dev, staging, production, etc.)
2. **Input**: How will users specify what to deploy? (current directory, specific path, Git ref)
3. **Authentication**: How will it authenticate? (API tokens, credentials, SSH keys)
4. **Output**: What feedback do users need? (deployment status, logs, URLs)
5. **Safety**: Should production deployments require confirmation?

Based on your answers, I'll design a complete CLI spec with commands, flags, and safety mechanisms."

*[After clarification, provide complete spec using the structure above]*

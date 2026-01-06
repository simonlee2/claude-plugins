# CLI Design Guidelines Reference

This reference points to authoritative CLI design resources.

## Primary Resource

**Command Line Interface Guidelines**
- Website: https://clig.dev/
- Repository: https://github.com/cli-guidelines/cli-guidelines

This comprehensive guide covers:
- Philosophy and principles of good CLI design
- Argument and flag conventions
- Output formatting and styling
- Error handling and exit codes
- Configuration and environment variables
- Interactivity and prompting
- Documentation and help text
- Subcommands and command organization
- Future-proofing and evolution

## Key Principles Summary

### 1. Human-First Design
- Make help easily discoverable
- Provide clear, actionable error messages
- Use colors and formatting to enhance readability (when appropriate)
- Design for both beginners and experts

### 2. Composability
- Output to stdout, errors to stderr
- Support piping and redirection
- Provide machine-readable output options (JSON, etc.)
- Exit with appropriate codes
- Respect standard input/output conventions

### 3. Consistency
- Follow POSIX conventions where appropriate
- Use standard flags (`--help`, `--version`, `--verbose`)
- Be consistent with popular tools
- Maintain internal consistency across subcommands

### 4. Robustness
- Validate input early
- Handle errors gracefully
- Provide meaningful error messages
- Support --dry-run for destructive operations
- Allow undo when possible

### 5. Discoverability
- Make help comprehensive but scannable
- Provide examples in documentation
- Use progressive disclosure (basic → advanced)
- Include man pages or comprehensive docs

## Standard Flag Conventions

### Information Flags
- `-h, --help` - Show help and exit
- `--version` - Show version information
- `-v, --verbose` - Enable verbose output
- `-q, --quiet` - Suppress non-essential output
- `--debug` - Enable debug mode

### Behavior Modifiers
- `-f, --force` - Skip confirmations, force action
- `-i, --interactive` - Enable interactive mode
- `-y, --yes` - Answer yes to all prompts
- `-n, --dry-run` - Simulate without making changes
- `--no-color` - Disable colored output

### Output Control
- `-o, --output <path>` - Specify output file
- `--format <type>` - Specify output format
- `--json` - Output as JSON
- `--pretty` - Human-friendly formatting

## Exit Code Conventions

```
0     Success
1     General error
2     Misuse (invalid arguments/flags)
64    Command line usage error (BSD convention)
65    Data format error
66    Cannot open input
69    Service unavailable
70    Internal software error
73    Cannot create output
74    I/O error
75    Temporary failure
77    Permission denied
78    Configuration error
130   Terminated by Ctrl+C (SIGINT)
```

## Output Best Practices

### Standard Output (stdout)
- Primary command output
- Machine-parseable results
- Piped data

### Standard Error (stderr)
- Error messages
- Warnings
- Progress indicators
- Diagnostic information
- Verbose/debug output

### Colors and Formatting
- Use ANSI colors when outputting to TTY
- Respect `NO_COLOR` environment variable
- Detect `TERM=dumb` and disable formatting
- Provide `--no-color` flag
- Use semantic colors (green=success, yellow=warning, red=error)

## Configuration Precedence

Standard precedence order (highest to lowest):
1. Command-line flags and arguments
2. Environment variables (typically prefixed with app name)
3. User configuration files (`~/.config/app/config`)
4. System configuration files (`/etc/app/config`)
5. Built-in defaults

## Interactive vs Non-Interactive

### When to Prompt
- TTY detected and not disabled
- Destructive operation without --force
- Ambiguous input requiring clarification
- Optional enhancement (e.g., creating config file)

### Non-Interactive Behavior
- Detect when stdin is not a TTY
- Provide `--no-input` or `--force` flags
- Exit with error if prompt needed but unavailable
- Support default values for prompts

## Error Message Guidelines

Good error messages should:
1. **State what went wrong** - Clearly identify the problem
2. **Explain why** - Help users understand the cause
3. **Suggest how to fix** - Provide actionable next steps
4. **Show context** - Include relevant details (file names, values)

### Examples

**Bad:**
```
Error: failed
```

**Good:**
```
Error: Cannot read config file '/home/user/.myapp/config.yml'
Reason: File does not exist
Fix: Run 'myapp init' to create a new config file, or use --config to specify a different location
```

## Help Text Structure

```
NAME
  command - brief description

SYNOPSIS
  command [global-options] <subcommand> [options] [arguments]

DESCRIPTION
  Longer description explaining what the command does and when to use it.

COMMANDS
  init        Initialize a new project
  build       Build the project
  deploy      Deploy to production

OPTIONS
  -h, --help        Show this help message
  --version         Show version information
  -v, --verbose     Enable verbose output
  -c, --config PATH Specify config file

EXAMPLES
  # Initialize a new project
  command init my-project

  # Build with custom config
  command build --config custom.yml

  # Deploy to production (with confirmation)
  command deploy --env production

SEE ALSO
  Documentation: https://example.com/docs
  Report issues: https://example.com/issues
```

## Subcommand Organization

For complex CLIs with multiple subcommands:

### Flat Structure (few commands)
```
mycli init
mycli build
mycli deploy
mycli status
```

### Grouped Structure (many commands)
```
mycli project init
mycli project delete

mycli build start
mycli build watch

mycli deploy staging
mycli deploy production
```

### Alias Support
```
mycli i      # Alias for 'init'
mycli b      # Alias for 'build'
mycli d      # Alias for 'deploy'
```

## Additional Resources

- **POSIX Utility Conventions**: https://pubs.opengroup.org/onlinepubs/9699919799/basedefs/V1_chap12.html
- **GNU Coding Standards**: https://www.gnu.org/prep/standards/html_node/Command_002dLine-Interfaces.html
- **12 Factor CLI Apps**: https://medium.com/@jdxcode/12-factor-cli-apps-dd3c227a0e46
- **CLI Guidelines**: https://github.com/cli-guidelines/cli-guidelines

## Testing Checklist

Test your CLI design:
- [ ] Help text is clear and comprehensive
- [ ] Works in TTY and non-TTY environments
- [ ] Respects NO_COLOR environment variable
- [ ] Handles Ctrl+C gracefully
- [ ] Validates input before executing
- [ ] Provides meaningful error messages
- [ ] Exit codes are appropriate
- [ ] Works with pipes and redirection
- [ ] Configuration precedence is correct
- [ ] Documentation is complete and accurate

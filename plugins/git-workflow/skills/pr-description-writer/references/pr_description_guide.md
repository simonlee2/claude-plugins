# Pull Request Description Guide

## Purpose of This Guide

This guide documents best practices for writing effective PR descriptions that help reviewers understand context and promote effective code reviews. A well-written PR description transforms a confusing diff into a coherent narrative about what changed and why.

## Core Principles

**1. Guide the reviewer through the code**
- Highlight related files and group them into concepts or problems being solved
- Help reviewers spend less time orienting themselves and more time reviewing effectively

**2. Provide high-level architectural context**
- Explain the "why" behind changes, not just the "what"
- Discuss architectural decisions and their implications

**3. Treat the reviewer as a customer**
- Make their job easier by providing strategic context
- Save them from having to hunt through the codebase or dig through docs

**4. Keep it concise enough to encourage genuine engagement**
- Overly verbose descriptions lead to skimming
- Balance comprehensiveness with readability

## Recommended PR Description Structure

### 1. Summary (2-3 sentences)
Brief, high-level overview of what the PR does and why it matters.

**Example:** "Implement new payment retry logic to reduce failed transaction recovery time from 24 hours to 5 minutes. This reduces customer support burden and improves checkout success rates."

### 2. Scope/Context (The "What" and "Why")
- Clearly state the motivation behind changes
- Link to related issues, domain logic, and prior discussions about alternatives
- Explain edge cases and constraints that influenced the approach
- Answer: What problem does this solve?

**Include:**
- References to related issues/PRs
- Context about why this change was needed
- Alternative approaches considered and why they were rejected
- Any constraints or limitations to be aware of

### 3. Implementation (The "How")
- Give a high-level description of program flow
- Highlight specific areas you want reviewers to pay close attention to
- Explain what may not be immediately obvious from the git diff
- Group related changes logically by component or concept

**Include:**
- Architecture decisions made
- Key data flow changes
- Any breaking changes or deprecations
- Notable implementation details

### 4. Review Priority & Navigation (For Large PRs)
When a PR is large or touches multiple components, provide a review entry point to help reviewers navigate efficiently.

**Include:**
- **Identify critical files first** – Call out which files contain the core logic changes. Reviewers should start here to understand the primary intent before examining supporting changes.
- **Group by concept** – Organize files into logical sections (e.g., "Core Feature Logic," "Tests," "Configuration," "Documentation") to show reviewers which files are most important.
- **Specify review order** – If changes depend on understanding certain files first, explicitly state the recommended review sequence.
- **Highlight risky or complex sections** – Flag files that introduce breaking changes, complex algorithms, or risky modifications that need extra attention.
- **Note supporting vs. core changes** – Clearly distinguish between essential changes and supporting changes (like tests, formatting, or documentation) so reviewers know where to allocate focus.

**Example format:**
```
## Files Changed (Review Priority)
- **Core** (start here):
  - `src/payments/RetryManager.ts` – New retry logic with exponential backoff
  - `src/payments/PaymentService.ts` – Updated to use new retry manager
- **Supporting**:
  - `tests/payments/*.test.ts` – Full test coverage for retry scenarios
  - `docs/PAYMENTS.md` – Updated documentation
- **Infrastructure**:
  - `.env.example` – New retry configuration variables
  - `migrations/` – Database schema for retry state tracking
```

### 5. Testing Strategy
Explain how reviewers can verify the changes work:
- Detail setup steps and test commands
- List which code areas were tested and which environments were validated
- Describe any new test cases added
- Explain any manual testing approach

**Include:**
- Commands to run tests
- Test coverage changes
- Edge cases tested
- Environment-specific testing notes

### 6. Visual Documentation (For UI/Behavioral Changes)
- Include before/after screenshots showing UI and behavioral differences
- Makes the reviewer's job significantly easier
- Especially important for frontend changes

### 7. Risk Assessment & Breaking Changes
- Explicitly call out breaking changes
- Flag downstream integration impacts or compatibility considerations
- Document any concerns about the implementation
- Note any deprecated APIs or migration paths

**Include:**
- Breaking changes for users/consumers
- Database migration risks
- Performance implications
- Backward compatibility considerations

## Best Practices

### For All PRs

1. **Start with a clear title** - Make it obvious what's being solved at a high level
2. **Use the git commits as your foundation** - Follow what the commits actually describe; don't invent a narrative
3. **Link to issues** - Use keywords like "Closes #123" to automatically link and close issues
4. **Keep related changes together** - Don't mix unrelated changes in the same PR
5. **Provide enough context** - Reviewers shouldn't have to hunt through docs or code

### For Large PRs (>400 lines)

1. **Always include a review priority section** - Reviewers need to know where to start
2. **Consider splitting into smaller PRs** - Reviewers can only effectively process 200-400 lines at a time
3. **Group changes by concept** - Don't just list every file changed; organize them logically
4. **Annotate with comments in the code** - Highlight why critical decisions were made
5. **Provide clear testing strategy** - Reviewers need to understand how to validate your work

### For Small PRs (<100 lines)

1. **Brief is okay** - A sentence or two of context plus the testing approach may suffice
2. **Still explain the "why"** - Even small changes benefit from context
3. **Don't over-explain** - Keep it concise and to the point

## Anti-Patterns to Avoid

- ❌ Leaving description blank or minimal
- ❌ Focusing only on code-level details without explaining architectural decisions
- ❌ Treating the description as merely a restatement of commit messages
- ❌ Writing vague descriptions that require reviewers to do detective work
- ❌ Burying critical file changes in a long list without calling them out
- ❌ Large PRs without guidance on what to review first
- ❌ Including deprecated code or commented-out sections without explanation
- ❌ Mixing formatting/cleanup changes with functional changes without separating them

## Impact on Code Review Quality

Research shows: **Code reviewers given good descriptions with context and reasoning gave significantly better feedback than those without.**

A context vacuum forces reviewers to:
- Request clarification before reviewing
- Search the codebase independently
- Make assumptions about intent
- Give cursory approvals ("LGTM 👍") due to lack of understanding

Comprehensive PR descriptions prevent these issues and lead to more meaningful feedback.

## Common Scenarios

### Scenario 1: New Feature
1. What problem does this feature solve?
2. What are the key user flows?
3. What architectural changes were required?
4. How do you test it?
5. Any performance or security considerations?

### Scenario 2: Bug Fix
1. What was the bug and how did it manifest?
2. What was the root cause?
3. How does your fix address it?
4. Could this bug have other manifestations?
5. How do you verify the fix works?

### Scenario 3: Refactoring
1. Why was this refactoring necessary?
2. What's different about the new approach?
3. Is this backwards compatible?
4. Are there any performance implications?
5. How do you verify functionality is preserved?

### Scenario 4: Dependency Update
1. What's being updated and why?
2. What's the breaking change (if any)?
3. What code had to change as a result?
4. Are there migration considerations?
5. How do you test compatibility?

## Tools and Integration

### GitHub PR Templates
Store a template in `.github/pull_request_template.md` to provide structure:

```markdown
## Summary
[2-3 sentences about what this PR does]

## Context
[Why is this change needed? What problem does it solve?]

## Implementation
[High-level description of the changes]

## Testing
[How to verify these changes work]

## Additional Notes
[Risk assessment, breaking changes, etc.]
```

### Using the Git Analysis Script
The `analyze_git_commits.py` script helps gather PR information:
- Lists all commits on your branch
- Shows which files were added, modified, or deleted
- Provides diff statistics
- Helps identify what's truly important to review

Run it to extract information for writing your PR description.

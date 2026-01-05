# Example: Weak Pull Request Description (Before Improvement)

## What Was Written

```
Updated payment handling

Changed the payment retry logic. Added new database table and updated service. See commits for details.

Files changed:
- RetryManager.ts
- PaymentService.ts
- PaymentRetry.ts
- migrations
- tests

All tests pass.
```

## Problems With This Description

1. **No context on "why"**
   - Reviewers don't understand what problem this solves
   - No link to the business need or issue
   - No mention of competitors or alternative approaches

2. **Vague summary**
   - "Updated payment handling" tells us nothing
   - Reviewers have to read the code to understand intent

3. **No file organization**
   - Just lists files without explaining which are critical
   - Reviewers don't know where to start
   - No distinction between core logic and supporting changes

4. **Insufficient testing details**
   - "All tests pass" doesn't explain what was tested
   - Reviewers can't understand how to validate manually
   - No edge cases mentioned

5. **Missing risk assessment**
   - Is this backwards compatible?
   - Any breaking changes?
   - Performance implications?

6. **Implementation details unclear**
   - What's the actual retry strategy?
   - Why this approach over alternatives?
   - What are the key architectural decisions?

## Result

- Reviewers give cursory approval without fully understanding the change
- Potential bugs are missed because context is lacking
- If something breaks in production, it's hard to understand why
- Knowledge about this feature is only in the author's head

## How It Should Be Improved

See `example_good_pr.md` for the same change described well.

### Key Improvements Made

1. ✅ Clear business context for why this change exists
2. ✅ High-level architecture explanation before code details
3. ✅ Files organized by importance and purpose
4. ✅ Detailed testing strategy with concrete steps
5. ✅ Explicit risk assessment and backwards compatibility notes
6. ✅ Design decisions explained with rationale
7. ✅ Issue links for traceability

This allows reviewers to give meaningful feedback instead of just approving.

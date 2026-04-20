---
name: quarterly-review
description: Generate a quarterly GitHub contributions review — monthly + per-repo breakdown and synthesized accomplishment narrative. Use when asked for "quarterly review", "Q1/Q2/Q3/Q4 review", "what did I ship this quarter", or "summarize my contributions". Works across personal repos and a specified org.
allowed-tools:
  - Bash
  - Read
  - Write
---

# Quarterly Review

Produce a structured review of the user's GitHub contributions for a given quarter. Combines raw totals (contributions API), per-repo/per-month breakdown (search API), and PR titles (for narrative synthesis).

## Inputs to resolve

Before running, confirm or infer:
- **Quarter** — e.g. `Q1 2026` → `2026-01-01..2026-03-31`. If year omitted, use current year.
- **GitHub user** — default to `gh api user --jq .login`.
- **Org(s)** — ask if not provided. Personal contributions are picked up automatically via the contributions API; org private repos need the search API.

Quarter → date range:
- Q1 = `01-01..03-31`
- Q2 = `04-01..06-30`
- Q3 = `07-01..09-30`
- Q4 = `10-01..12-31`

Only ask follow-up questions if the quarter or org is ambiguous. Proceed with reasonable defaults otherwise.

## Steps

### 1. Totals across all accessible repos (contributions API)

```bash
gh api graphql -f query='
{
  user(login: "<USER>") {
    contributionsCollection(from: "<FROM>T00:00:00Z", to: "<TO>T23:59:59Z") {
      totalCommitContributions
      totalPullRequestContributions
      totalPullRequestReviewContributions
      totalIssueContributions
      totalRepositoryContributions
      commitContributionsByRepository(maxRepositories: 50) {
        repository { nameWithOwner }
        contributions { totalCount }
      }
    }
  }
}'
```

Note: private org contributions often don't appear here — use step 2.

### 2. Org PRs + reviews (search API)

```bash
# PRs authored
gh search prs --author <USER> --owner <ORG> \
  --created <FROM>..<TO> --limit 300 \
  --json repository,state,title,createdAt,url,number > /tmp/qreview_prs.json

# PRs reviewed
gh api graphql -f query='
{
  search(query: "reviewed-by:<USER> org:<ORG> updated:<FROM>..<TO>", type: ISSUE, first: 100) {
    issueCount
  }
}'
```

If the org list is multiple, run per-org and concatenate.

### 3. Breakdowns

**Monthly totals:**
```bash
jq -r 'group_by(.createdAt[0:7]) | map({
  month: .[0].createdAt[0:7],
  total: length,
  merged: map(select(.state == "merged")) | length
}) | .[] | "\(.month): \(.total) PRs (\(.merged) merged)"' /tmp/qreview_prs.json
```

**Per-repo totals:**
```bash
jq -r 'group_by(.repository.nameWithOwner) | map({
  repo: .[0].repository.nameWithOwner,
  total: length,
  merged: map(select(.state == "merged")) | length,
  open: map(select(.state == "open")) | length,
  closed: map(select(.state == "closed")) | length
}) | sort_by(-.total) | .[] | "\(.repo)\t\(.total)\t\(.merged)\t\(.open)\t\(.closed)"' /tmp/qreview_prs.json
```

**Month × repo matrix:**
```bash
jq -r 'group_by(.createdAt[0:7]) | .[] |
  "=== \(.[0].createdAt[0:7]) ===",
  (group_by(.repository.nameWithOwner) | sort_by(-length) | .[] |
    "  \(.[0].repository.nameWithOwner): \(length)")' /tmp/qreview_prs.json
```

### 4. Pull titles for narrative synthesis

```bash
jq -r '.[] | "\(.createdAt[0:7])\t\(.repository.nameWithOwner)\t\(.state)\t#\(.number)\t\(.title)"' \
  /tmp/qreview_prs.json | sort
```

Read all titles. **Do not** just list them back — synthesize. Group titles into themes:
- Major feature launches (new products, end-to-end shipped flows)
- Infrastructure / platform work (build systems, CI, migrations)
- Model / integration migrations (e.g., Gemini → Nanobanana, Opus 4.6)
- UX polish & perf
- New projects (repos with first commits in the quarter)
- Quality: tests, evals, observability

## Output format

```
## <Quarter> Overview — @<user> @ <org>

**Monthly:**
- Month 1: N PRs (M merged)
- Month 2: ...
- Total: X authored, Y merged, Z reviewed

**By month × repo:**
| Repo | M1 | M2 | M3 |
|---|--:|--:|--:|
...

### Key accomplishments

**1. <Theme headline>** — short paragraph + bullets
**2. ...**

**Bottom line:** 1-2 sentences capturing the arc of the quarter.
```

## Style rules

- Be concise; sacrifice grammar for compactness (user preference).
- Lead with numbers, then themes, then narrative.
- Always cite merge rate (`merged / authored`) — it's a quality signal.
- Flag new repos (first PR in the quarter) — those are launches.
- Don't bury the biggest theme — open with it.
- Offer follow-ups at the end: LOC, commit counts, review breakdown, per-month deep dive.

## Common gotchas

- `gh search prs` state values are **lowercase** (`merged`, `open`, `closed`), not `MERGED`.
- `mergedAt` is **not** a valid `--json` field for `gh search prs`. Use `state == "merged"` instead.
- The contributions GraphQL API returns `0` for org private repos unless the viewer is a member and has "Include private contributions on profile" enabled. Always back it up with the search API.
- `--limit 300` caps results; if `issueCount` exceeds 300, paginate or narrow the window.

---
name: marketplace-sync
description: This skill should be used when the user asks to "update the marketplace", "refresh the github page", "sync plugins.json", "update docs/plugins.json", or mentions keeping the GitHub Pages site in sync with plugin changes.
---

# Marketplace Sync

## Overview

This skill updates the GitHub Pages marketplace (`docs/plugins.json`) by intelligently combining automated scanning with AI-generated marketing copy. It extracts technical metadata from plugin files, then generates compelling icons, taglines, and categories based on the plugin's purpose and capabilities.

## When to Use This Skill

Use this skill when:
- User asks to "update the marketplace"
- User asks to "refresh the github page" or "sync the website"
- User asks to "sync plugins.json" or "update docs/plugins.json"
- After making changes to plugins that should be reflected on the website
- After adding new plugins to the repository
- After updating plugin versions or components

## How It Works

### Phase 1: Automated Scanning

Run `scripts/sync-marketplace.py` to extract technical metadata:

1. **Scan plugin directories** (`plugins/*/`) for all installed plugins
2. **Read metadata** from each plugin's `.claude-plugin/plugin.json`
3. **Extract component information**:
   - Commands from `commands/*.md` files
   - Skills from `skills/*/SKILL.md` files
   - Agents from `agents/*/AGENT.md` files
4. **Preserve existing marketing copy** for unchanged plugins
5. **Report changes**: Show what was added, updated, or removed

### Phase 2: Intelligent Marketing Copy Generation

After running the script, analyze the results and generate compelling marketing copy:

**For new plugins:**
1. Read the plugin's description and SKILL.md files to understand its purpose
2. Generate an appropriate **icon emoji** that visually represents the plugin's function
3. Write a compelling **tagline** (under 60 characters) that captures the value proposition
4. Assign relevant **categories** based on the plugin's domain and use cases
5. Document any **requirements** (API keys, environment variables)

**For updated plugins:**
1. Review what changed (version bumps, new components, updated descriptions)
2. Consider if the existing marketing copy is still accurate
3. Update taglines or categories if the plugin's scope has expanded
4. Preserve marketing copy if changes are minor (version bumps, small tweaks)

### Phase 3: Update and Commit

Write the updated `docs/plugins.json` with both technical metadata and polished marketing copy.

## Usage

### Intelligent Update Workflow

When the user asks to "update the marketplace", follow this workflow:

**1. Run the sync script:**
```bash
python3 skills/marketplace-sync/scripts/sync-marketplace.py
```

**2. Analyze the output:**
```
➕ New plugin: data-analyzer
➖ Removed plugin: old-plugin
📝 git-workflow: skills changed from 1 to 2
```

**3. For new plugins:**
- Read the plugin's files to understand its purpose
- Generate appropriate icon, tagline, and categories
- Update `docs/plugins.json` with the marketing copy

**4. For removed plugins:**
- Confirm the plugin directory was intentionally deleted
- Note that it will be removed from the marketplace automatically
- No action needed (script handles removal)

**5. For updated plugins:**
- Review the changes (new components, version bumps)
- Assess if marketing copy needs updating
- Update if scope/purpose has changed significantly

**6. Show the user what you generated:**
- Explain the icon choice for new plugins
- Share the tagline and categories
- Confirm removals were intentional
- Ask for feedback if unsure

### Example: New Plugin Detected

```bash
$ python3 skills/marketplace-sync/scripts/sync-marketplace.py
➕ New plugin: data-analyzer
```

**Your response:**
"I've detected a new plugin called 'data-analyzer'. Let me read its documentation and generate marketing copy..."

*[Read plugin.json and SKILL.md files]*

"Based on the plugin's purpose (analyzing data patterns), I've generated:
- Icon: 📊 (represents data/analytics)
- Tagline: 'Discover patterns and insights in your data'
- Categories: ['data', 'analytics', 'productivity']

Updating the marketplace now..."

*[Update docs/plugins.json with generated copy]*

### What Gets Updated Automatically

**From plugin files (auto-extracted):**
- Plugin name, version, author
- Plugin description
- Component names and descriptions
- Component counts (commands, skills, agents)
- Installation command

**Preserved from existing data (manual marketing copy):**
- Plugin icons (emoji)
- Plugin taglines
- Plugin categories
- Requirements (API keys, etc.)
- Skill features (bullet points)
- Skill examples

### Generating Marketing Copy for New Plugins

When the script detects a new plugin with default values (📦 icon, generic tagline), intelligently generate better marketing copy:

**Step 1: Understand the Plugin**
Read the plugin's materials to understand its purpose:
- Plugin description from `plugin.json`
- SKILL.md files to understand capabilities
- Command descriptions to see functionality
- Examples and use cases from documentation

**Step 2: Choose an Appropriate Icon**
Select an emoji that visually represents the plugin's function:

Examples:
- Git/workflow tools: 🔧 (wrench), 🔀 (shuffle), 📋 (clipboard)
- Creative/AI tools: 🎨 (palette), ✨ (sparkles), 🖼️ (framed picture)
- Data/analytics: 📊 (chart), 🔍 (magnifying glass), 📈 (trending up)
- Security/validation: 🔒 (lock), ✅ (checkmark), 🛡️ (shield)
- Documentation: 📚 (books), 📝 (memo), 📖 (open book)
- DevOps/automation: 🤖 (robot), ⚙️ (gear), 🚀 (rocket)

**Step 3: Write a Compelling Tagline**
Create a benefit-focused tagline under 60 characters:

Good taglines:
- Focus on the benefit, not just what it is
- Use active, engaging language
- Capture the unique value proposition
- "Streamline your git operations with intelligent automation" ✅
- "AI-powered image generation and transformation" ✅

Avoid:
- Generic descriptions that could apply to anything
- "Git workflow automation tools" ❌ (too dry)
- "Tools for images" ❌ (too vague)

**Step 4: Assign Relevant Categories**
Choose 2-4 categories that help users find the plugin:

Common categories:
- `productivity`, `workflow`, `automation`
- `git`, `version-control`, `github`
- `ai`, `creative`, `images`, `generation`
- `testing`, `quality`, `validation`
- `documentation`, `writing`, `content`
- `security`, `privacy`, `compliance`
- `data`, `analytics`, `reporting`

**Step 5: Document Requirements**
List any setup requirements:
- Environment variables (API keys, tokens)
- External services or accounts needed
- System dependencies
- Configuration prerequisites

**Step 6: Update the JSON**
After generating marketing copy, read the current `docs/plugins.json`, update the specific plugin entry with your generated content, and write the file back.

## Understanding the Output

The script reports changes in this format:

```
🔍 Scanning plugins...

📊 Detected 3 change(s):
  ➕ New plugin: My Plugin
  🔄 git-workflow: 1.0.0 → 1.1.0
  📝 creative-tools: skills changed from 1 to 2

💾 Writing to /path/to/docs/plugins.json...
✅ Marketplace data updated successfully!
```

**Change indicators:**
- `➕ New plugin` - A new plugin was discovered in `plugins/`
- `➖ Removed plugin` - A plugin directory was deleted (will be removed from marketplace)
- `🔄 Version change` - Plugin version was updated in `plugin.json`
- `📝 Component change` - Number of commands/skills/agents changed

**Handling Removals:**
When a plugin directory is deleted from `plugins/`, the script:
1. Detects it's missing from the new scan
2. Reports `➖ Removed plugin: PluginName`
3. Removes it from `docs/plugins.json` automatically
4. The marketplace site will no longer show the removed plugin

## Workflow Integration

### Before Pushing to GitHub

After making plugin changes, update the marketplace before committing:

```bash
# 1. Make plugin changes
# 2. Update the marketplace
python skills/marketplace-sync/scripts/sync-marketplace.py

# 3. Review changes
git diff docs/plugins.json

# 4. Commit everything together
git add .
git commit -m "Add new feature and update marketplace"
git push
```

### After Adding a New Plugin

When adding a new plugin to the repository:

```bash
# 1. Create plugin structure
mkdir -p plugins/my-plugin/{.claude-plugin,skills,commands}

# 2. Add plugin.json and components
# ... create your plugin files ...

# 3. Sync marketplace (auto-discovers new plugin)
python skills/marketplace-sync/scripts/sync-marketplace.py

# 4. Customize marketing copy in docs/plugins.json
# Edit: icon, tagline, categories

# 5. Sync again to verify preservation
python skills/marketplace-sync/scripts/sync-marketplace.py

# 6. Commit
git add .
git commit -m "Add my-plugin to marketplace"
```

## Script Details

### Location

`scripts/sync-marketplace.py`

### How It Scans Plugins

**Plugin metadata** from `.claude-plugin/plugin.json`:
```json
{
  "name": "plugin-name",
  "description": "Plugin description",
  "version": "1.0.0",
  "author": {"name": "Simon"}
}
```

**Commands** from `commands/*.md` frontmatter:
```yaml
---
description: Command description here
---
```

**Skills** from `skills/*/SKILL.md` frontmatter:
```yaml
---
name: skill-name
description: Skill description here
---
```

**Agents** from `agents/*/AGENT.md` frontmatter:
```yaml
---
name: agent-name
description: Agent description here
---
```

### Data Merging Strategy

1. **Load existing** `docs/plugins.json` to preserve marketing copy
2. **Scan plugins** to extract fresh technical metadata
3. **Merge by plugin ID**:
   - Use scanned data for: name, version, description, components
   - Preserve existing data for: icon, tagline, categories, requirements
4. **Write updated** `docs/plugins.json`

This ensures marketing copy survives updates while technical metadata stays current.

## Best Practices

### Regular Syncing

Run the sync after any plugin changes:
- ✅ After updating plugin versions
- ✅ After adding/removing components
- ✅ After changing descriptions
- ✅ Before creating commits

### Marketing Copy Maintenance

Keep marketing copy fresh:
- Choose distinctive emojis that represent each plugin
- Write compelling taglines (under 60 characters)
- Add relevant categories for filtering
- Document requirements (API keys, environment setup)

### Version Management

When bumping plugin versions:
1. Update `plugin.json` version field
2. Run sync script (auto-detects version change)
3. Review changes in git diff
4. Commit together with code changes

## Troubleshooting

**Script shows no changes but I made updates:**
- Verify you edited the correct files (plugin.json, SKILL.md frontmatter)
- Check that frontmatter uses correct YAML format (`---` delimiters)
- Ensure files are in expected directories

**New plugin not detected:**
- Verify `.claude-plugin/plugin.json` exists
- Check that plugin directory is in `plugins/`
- Ensure plugin.json has valid JSON syntax

**Marketing copy was overwritten:**
- The script preserves: icon, tagline, categories, requirements
- If overwritten, check if plugin ID changed (treated as new plugin)
- Manually restore from git history and re-run sync

**Component counts incorrect:**
- Verify SKILL.md files are in `skills/*/SKILL.md` format
- Check command files are in `commands/*.md` format
- Ensure frontmatter has `---` delimiters

## Implementation Notes

The sync script is written in Python 3 with no external dependencies. It uses:
- `pathlib` for cross-platform path handling
- `json` for data serialization
- `re` for pattern matching (extracting features/examples)

The script is designed to be:
- **Idempotent**: Running multiple times with no changes shows "no changes detected"
- **Non-destructive**: Always preserves marketing copy
- **Informative**: Reports exactly what changed
- **Standalone**: No external dependencies required

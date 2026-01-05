# Simon's Claude Code Plugins

Personal collection of Claude Code plugins for development workflow automation and creative tools.

## Available Plugins

### 🔧 git-workflow

Git workflow automation tools for efficient development.

**Components:**
- **Command:** `/git-workflow:commit-push` - Commit and push changes without creating a PR
- **Skill:** `pr-description-writer` - Generate comprehensive PR descriptions from git commits

**Use cases:**
- Quick commits with smart message generation
- Creating reviewer-friendly PR descriptions
- Updating PR descriptions after new commits

### 🎨 creative-tools

AI-powered creative tools using state-of-the-art models.

**Components:**
- **Skill:** `nanobanana-image-gen` - Generate and edit images using Google's Nanobanana model via Replicate API

**Capabilities:**
- Text-to-image generation
- Image-to-image transformations
- Style transfers and variations
- Custom aspect ratios (1:1, 16:9, 9:16, 4:3, etc.)
- Multiple image input support

**Requirements:**
- `REPLICATE_API_KEY` environment variable (get yours at https://replicate.com/account/api-tokens)

## Installation

### For Personal Use (All Your Systems)

1. **Add the marketplace:**
   ```bash
   /plugin marketplace add simon-username/claude-plugins
   ```
   *(Replace `simon-username` with your GitHub username once you push this to GitHub)*

2. **Install plugins:**
   ```bash
   # Install both plugins
   /plugin install git-workflow@simon-plugins
   /plugin install creative-tools@simon-plugins

   # Or install individually
   /plugin install git-workflow@simon-plugins
   ```

### For Others to Use

Anyone can install your plugins by:
```bash
/plugin marketplace add simon-username/claude-plugins
/plugin install git-workflow@simon-plugins
```

### Local Testing (Before Publishing)

```bash
# Add marketplace from local directory
/plugin marketplace add ~/Developer/claude-plugins

# Install plugins locally
/plugin install git-workflow@simon-plugins
/plugin install creative-tools@simon-plugins
```

## Usage

### git-workflow

**Commit and push:**
```
/git-workflow:commit-push
```
Claude will analyze your changes, create a commit with a smart message, and push to remote.

**Generate PR description:**
Just ask: "Write a PR description for my changes" and the `pr-description-writer` skill will automatically activate.

### creative-tools

**Generate images:**
```
Generate a 16:9 banner image of a sunset over mountains
```

**Transform images:**
```
Make this photo look like a watercolor painting
```

The `nanobanana-image-gen` skill activates automatically when you request image generation or transformation.

## Publishing to GitHub

1. **Initialize git repo:**
   ```bash
   cd ~/Developer/claude-plugins
   git init
   git add .
   git commit -m "Initial commit: Add git-workflow and creative-tools plugins"
   ```

2. **Create GitHub repo:**
   - Go to https://github.com/new
   - Create a new public repository named `claude-plugins`

3. **Push to GitHub:**
   ```bash
   git remote add origin git@github.com:your-username/claude-plugins.git
   git branch -M main
   git push -u origin main
   ```

4. **Install from GitHub:**
   ```bash
   /plugin marketplace add your-username/claude-plugins
   ```

## Directory Structure

```
claude-plugins/
├── .claude-plugin/
│   └── marketplace.json          # Marketplace catalog
├── plugins/
│   ├── git-workflow/
│   │   ├── .claude-plugin/
│   │   │   └── plugin.json
│   │   ├── commands/
│   │   │   └── commit-push.md
│   │   └── skills/
│   │       └── pr-description-writer/
│   │           ├── SKILL.md
│   │           ├── scripts/
│   │           ├── references/
│   │           └── assets/
│   └── creative-tools/
│       ├── .claude-plugin/
│       │   └── plugin.json
│       └── skills/
│           └── nanobanana-image-gen/
│               ├── SKILL.md
│               ├── scripts/
│               └── references/
├── README.md
└── LICENSE

```

## Adding New Components

### Add a new command to git-workflow:
```bash
# Create the command file
touch ~/Developer/claude-plugins/plugins/git-workflow/commands/my-command.md
```

### Add a new skill to creative-tools:
```bash
# Create the skill directory
mkdir -p ~/Developer/claude-plugins/plugins/creative-tools/skills/my-skill
touch ~/Developer/claude-plugins/plugins/creative-tools/skills/my-skill/SKILL.md
```

### Create a new plugin:
```bash
# Create plugin structure
mkdir -p ~/Developer/claude-plugins/plugins/my-plugin/{.claude-plugin,commands,skills,agents}

# Create plugin.json
cat > ~/Developer/claude-plugins/plugins/my-plugin/.claude-plugin/plugin.json << 'EOF'
{
  "name": "my-plugin",
  "description": "Description of my plugin",
  "version": "1.0.0",
  "author": {
    "name": "Simon"
  }
}
EOF

# Add to marketplace.json plugins array
```

## Version Management

When updating plugins:
1. Update the version in `plugin.json`
2. Update the version in `marketplace.json`
3. Commit and push changes
4. Users can update with `/plugin update plugin-name@simon-plugins`

## License

MIT (or your preferred license)

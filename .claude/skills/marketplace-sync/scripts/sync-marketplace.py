#!/usr/bin/env python3
"""
Marketplace Sync Script

Scans plugin directories and generates/updates docs/plugins.json with the latest
metadata while preserving marketing copy (icons, taglines, categories).
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, List, Any


def parse_frontmatter(content: str) -> Dict[str, str]:
    """Extract YAML frontmatter from markdown content."""
    frontmatter = {}
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            frontmatter_text = parts[1].strip()
            for line in frontmatter_text.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    frontmatter[key.strip()] = value.strip()
    return frontmatter


def read_plugin_metadata(plugin_path: Path) -> Dict[str, Any]:
    """Read metadata from plugin.json."""
    plugin_json = plugin_path / '.claude-plugin' / 'plugin.json'
    if not plugin_json.exists():
        return None

    with open(plugin_json, 'r') as f:
        return json.load(f)


def scan_commands(plugin_path: Path) -> List[Dict[str, Any]]:
    """Scan and extract command metadata."""
    commands = []
    commands_dir = plugin_path / 'commands'

    if not commands_dir.exists():
        return commands

    for cmd_file in commands_dir.glob('*.md'):
        with open(cmd_file, 'r') as f:
            content = f.read()
            frontmatter = parse_frontmatter(content)

            if frontmatter:
                command_name = cmd_file.stem
                commands.append({
                    'name': command_name,
                    'fullName': f'/{plugin_path.name}:{command_name}',
                    'description': frontmatter.get('description', ''),
                    'usage': f'Run the command and Claude will handle the rest',
                    'example': f'/{plugin_path.name}:{command_name}'
                })

    return commands


def scan_skills(plugin_path: Path) -> List[Dict[str, Any]]:
    """Scan and extract skill metadata."""
    skills = []
    skills_dir = plugin_path / 'skills'

    if not skills_dir.exists():
        return skills

    for skill_dir in skills_dir.iterdir():
        if not skill_dir.is_dir():
            continue

        skill_md = skill_dir / 'SKILL.md'
        if not skill_md.exists():
            continue

        with open(skill_md, 'r') as f:
            content = f.read()
            frontmatter = parse_frontmatter(content)

            if frontmatter:
                skill_name = frontmatter.get('name', skill_dir.name)
                description = frontmatter.get('description', '')

                # Extract usage hint from description
                usage = "Activates automatically based on your request"
                if 'user asks' in description.lower():
                    usage = "Just ask naturally and the skill activates automatically"

                skill_data = {
                    'name': skill_name,
                    'fullName': f'{plugin_path.name}:{skill_name}',
                    'description': description,
                    'usage': usage
                }

                # Extract features from the markdown body
                features = extract_features_from_content(content)
                if features:
                    skill_data['features'] = features

                # Extract examples from the markdown body
                examples = extract_examples_from_content(content)
                if examples:
                    skill_data['examples'] = examples

                skills.append(skill_data)

    return skills


def scan_agents(plugin_path: Path) -> List[Dict[str, Any]]:
    """Scan and extract agent metadata."""
    agents = []
    agents_dir = plugin_path / 'agents'

    if not agents_dir.exists():
        return agents

    for agent_dir in agents_dir.iterdir():
        if not agent_dir.is_dir():
            continue

        agent_md = agent_dir / 'AGENT.md'
        if not agent_md.exists():
            continue

        with open(agent_md, 'r') as f:
            content = f.read()
            frontmatter = parse_frontmatter(content)

            if frontmatter:
                agents.append({
                    'name': frontmatter.get('name', agent_dir.name),
                    'fullName': f'{plugin_path.name}:{agent_dir.name}',
                    'description': frontmatter.get('description', ''),
                    'usage': 'Triggered automatically by the Task tool when appropriate'
                })

    return agents


def extract_features_from_content(content: str) -> List[str]:
    """Extract bullet point features from markdown content."""
    features = []

    # Look for sections that might contain features
    lines = content.split('\n')
    in_features_section = False

    for line in lines:
        # Detect features sections
        if any(keyword in line.lower() for keyword in ['## capabilities', '## features', '## core capabilities']):
            in_features_section = True
            continue

        # Stop at next major section
        if line.startswith('## ') and in_features_section:
            in_features_section = False

        # Extract bullet points in features section
        if in_features_section and line.strip().startswith(('-', '*', '•')):
            feature = line.strip().lstrip('-*• ').strip()
            if feature and len(feature) < 200:  # Reasonable feature length
                features.append(feature)
                if len(features) >= 5:  # Limit to 5 features
                    break

    return features


def extract_examples_from_content(content: str) -> List[str]:
    """Extract example usage from markdown content."""
    examples = []

    # Look for example sections
    lines = content.split('\n')
    in_examples_section = False

    for line in lines:
        # Detect examples sections
        if any(keyword in line.lower() for keyword in ['example request', '**example', 'examples:']):
            in_examples_section = True
            continue

        # Stop at next major section
        if line.startswith('##') and in_examples_section:
            in_examples_section = False

        # Extract quoted examples or bullet points
        if in_examples_section:
            # Look for quoted text
            quoted = re.findall(r'"([^"]+)"', line)
            for quote in quoted:
                if 10 < len(quote) < 200:  # Reasonable example length
                    examples.append(quote)
                    if len(examples) >= 3:  # Limit to 3 examples
                        return examples

            # Or bullet points
            if line.strip().startswith(('-', '*', '•')):
                example = line.strip().lstrip('-*• ').strip()
                if example and 10 < len(example) < 200:
                    examples.append(example)
                    if len(examples) >= 3:
                        return examples

    return examples


def load_existing_marketplace(docs_path: Path) -> Dict[str, Any]:
    """Load existing marketplace data to preserve marketing copy."""
    plugins_json = docs_path / 'plugins.json'
    if plugins_json.exists():
        with open(plugins_json, 'r') as f:
            return json.load(f)
    return {'marketplace': {}, 'plugins': []}


def merge_plugin_data(existing: Dict[str, Any], scanned: Dict[str, Any]) -> Dict[str, Any]:
    """Merge scanned data with existing marketing copy."""
    # Start with scanned data
    merged = scanned.copy()

    # Preserve marketing fields from existing data if they exist
    if existing:
        marketing_fields = ['icon', 'tagline', 'categories', 'requirements']
        for field in marketing_fields:
            if field in existing:
                merged[field] = existing[field]

    return merged


def generate_marketplace_data(repo_root: Path) -> Dict[str, Any]:
    """Generate complete marketplace data by scanning plugins."""
    plugins_dir = repo_root / 'plugins'
    docs_dir = repo_root / 'docs'

    # Load existing data to preserve marketing copy
    existing_data = load_existing_marketplace(docs_dir)
    existing_plugins = {p['id']: p for p in existing_data.get('plugins', [])}

    # Scan all plugins
    plugins = []
    for plugin_path in plugins_dir.iterdir():
        if not plugin_path.is_dir():
            continue

        # Read plugin metadata
        metadata = read_plugin_metadata(plugin_path)
        if not metadata:
            continue

        # Scan components
        commands = scan_commands(plugin_path)
        skills = scan_skills(plugin_path)
        agents = scan_agents(plugin_path)

        # Build plugin data
        plugin_data = {
            'id': metadata.get('name', plugin_path.name),
            'name': metadata.get('name', plugin_path.name).replace('-', ' ').title(),
            'namespace': 'simon-plugins',
            'description': metadata.get('description', ''),
            'version': metadata.get('version', '1.0.0'),
            'author': metadata.get('author', {}).get('name', 'Simon'),
            'installation': f"/plugin install {metadata.get('name')}@simon-plugins",
            'components': {}
        }

        # Add components
        if commands:
            plugin_data['components']['commands'] = commands
        if skills:
            plugin_data['components']['skills'] = skills
        if agents:
            plugin_data['components']['agents'] = agents

        # Merge with existing data to preserve marketing copy
        plugin_id = plugin_data['id']
        if plugin_id in existing_plugins:
            plugin_data = merge_plugin_data(existing_plugins[plugin_id], plugin_data)
        else:
            # New plugin - set defaults for marketing fields
            plugin_data['icon'] = '📦'
            plugin_data['tagline'] = plugin_data['description'][:60] + '...' if len(plugin_data['description']) > 60 else plugin_data['description']
            plugin_data['categories'] = ['productivity']

        plugins.append(plugin_data)

    # Build complete marketplace data
    marketplace_data = {
        'marketplace': existing_data.get('marketplace', {
            'name': "Simon's Claude Plugins",
            'namespace': 'simon-plugins',
            'repository': 'simonlee2/claude-plugins',
            'description': 'Professional Claude Code plugins for development workflow automation and creative tools'
        }),
        'plugins': plugins
    }

    return marketplace_data


def detect_changes(old_data: Dict[str, Any], new_data: Dict[str, Any]) -> List[str]:
    """Detect and summarize changes between old and new marketplace data."""
    changes = []

    old_plugins = {p['id']: p for p in old_data.get('plugins', [])}
    new_plugins = {p['id']: p for p in new_data.get('plugins', [])}

    # Check for new plugins
    for plugin_id in new_plugins:
        if plugin_id not in old_plugins:
            changes.append(f"➕ New plugin: {new_plugins[plugin_id]['name']}")

    # Check for removed plugins
    for plugin_id in old_plugins:
        if plugin_id not in new_plugins:
            changes.append(f"➖ Removed plugin: {old_plugins[plugin_id]['name']}")

    # Check for version changes and component changes
    for plugin_id in new_plugins:
        if plugin_id in old_plugins:
            old_plugin = old_plugins[plugin_id]
            new_plugin = new_plugins[plugin_id]

            # Version change
            if old_plugin.get('version') != new_plugin.get('version'):
                changes.append(f"🔄 {new_plugin['name']}: {old_plugin.get('version')} → {new_plugin.get('version')}")

            # Component changes
            old_components = old_plugin.get('components', {})
            new_components = new_plugin.get('components', {})

            for comp_type in ['commands', 'skills', 'agents']:
                old_count = len(old_components.get(comp_type, []))
                new_count = len(new_components.get(comp_type, []))

                if old_count != new_count:
                    changes.append(f"  📝 {new_plugin['name']}: {comp_type} changed from {old_count} to {new_count}")

    return changes


def main():
    """Main execution function."""
    # Determine repository root
    # Path: sync-marketplace.py -> scripts/ -> marketplace-sync/ -> skills/ -> .claude/ -> repo_root
    repo_root = Path(__file__).parent.parent.parent.parent.parent
    docs_dir = repo_root / 'docs'
    plugins_json = docs_dir / 'plugins.json'

    print("🔍 Scanning plugins...")

    # Load existing data
    existing_data = load_existing_marketplace(docs_dir)

    # Generate new marketplace data
    new_data = generate_marketplace_data(repo_root)

    # Detect changes
    changes = detect_changes(existing_data, new_data)

    if not changes:
        print("✅ No changes detected - marketplace is up to date")
        return

    print(f"\n📊 Detected {len(changes)} change(s):")
    for change in changes:
        print(f"  {change}")

    # Write updated data
    print(f"\n💾 Writing to {plugins_json}...")
    with open(plugins_json, 'w') as f:
        json.dump(new_data, f, indent=2)

    print("✅ Marketplace data updated successfully!")
    print(f"\n📍 Updated: {plugins_json}")


if __name__ == '__main__':
    main()

// ============================================
// State Management
// ============================================
let pluginsData = null;
let currentFilter = 'all';
let searchQuery = '';

// ============================================
// Initialization
// ============================================
document.addEventListener('DOMContentLoaded', async () => {
    await loadPlugins();
    setupEventListeners();
    renderPlugins();
    updateCounts();
    startTerminalAnimation();
});

// ============================================
// Data Loading
// ============================================
async function loadPlugins() {
    try {
        const response = await fetch('plugins.json');
        pluginsData = await response.json();
    } catch (error) {
        console.error('Failed to load plugins:', error);
        pluginsData = { plugins: [] };
    }
}

// ============================================
// Utility - Safe HTML Escaping
// ============================================
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ============================================
// Event Listeners
// ============================================
function setupEventListeners() {
    // Search input
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            searchQuery = e.target.value.toLowerCase();
            renderPlugins();
        });
    }

    // Filter buttons
    const filterButtons = document.querySelectorAll('.filter-tag');
    filterButtons.forEach(button => {
        button.addEventListener('click', () => {
            filterButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
            currentFilter = button.getAttribute('data-filter');
            renderPlugins();
        });
    });

    // Close modal on escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            closeModal();
        }
    });
}

// ============================================
// Terminal Animation
// ============================================
function startTerminalAnimation() {
    const typedText = document.querySelector('.typed-text');
    if (typedText) {
        const text = typedText.getAttribute('data-text');
        typedText.textContent = text;
    }
}

// ============================================
// Rendering Functions
// ============================================
function renderPlugins() {
    const pluginsGrid = document.getElementById('pluginsGrid');
    if (!pluginsGrid || !pluginsData) return;

    const filteredPlugins = filterPlugins();

    // Clear existing content
    pluginsGrid.innerHTML = '';

    if (filteredPlugins.length === 0) {
        const emptyState = document.createElement('div');
        emptyState.style.cssText = 'grid-column: 1 / -1; text-align: center; padding: 3rem;';
        const message = document.createElement('p');
        message.style.cssText = 'color: var(--color-text-muted); font-size: 1.125rem;';
        message.textContent = 'No plugins found matching your criteria.';
        emptyState.appendChild(message);
        pluginsGrid.appendChild(emptyState);
        return;
    }

    filteredPlugins.forEach((plugin, index) => {
        const card = createPluginCard(plugin, index);
        pluginsGrid.appendChild(card);
    });
}

function createPluginCard(plugin, index) {
    const commandsCount = plugin.components.commands?.length || 0;
    const skillsCount = plugin.components.skills?.length || 0;
    const agentsCount = plugin.components.agents?.length || 0;

    const card = document.createElement('div');
    card.className = 'plugin-card';
    card.style.animationDelay = `${index * 0.1}s`;
    card.onclick = () => openPluginModal(plugin.id);

    // Header
    const header = document.createElement('div');
    header.className = 'plugin-header';

    const icon = document.createElement('div');
    icon.className = 'plugin-icon';
    icon.textContent = plugin.icon;

    const headerContent = document.createElement('div');
    headerContent.className = 'plugin-header-content';

    const name = document.createElement('h3');
    name.className = 'plugin-name';
    name.textContent = plugin.name;

    const tagline = document.createElement('p');
    tagline.className = 'plugin-tagline';
    tagline.textContent = plugin.tagline;

    headerContent.appendChild(name);
    headerContent.appendChild(tagline);
    header.appendChild(icon);
    header.appendChild(headerContent);

    // Description
    const description = document.createElement('p');
    description.className = 'plugin-description';
    description.textContent = plugin.description;

    // Stats
    const stats = document.createElement('div');
    stats.className = 'plugin-stats';

    if (commandsCount > 0) {
        stats.appendChild(createStat(commandsCount, `Command${commandsCount !== 1 ? 's' : ''}`));
    }
    if (skillsCount > 0) {
        stats.appendChild(createStat(skillsCount, `Skill${skillsCount !== 1 ? 's' : ''}`));
    }
    if (agentsCount > 0) {
        stats.appendChild(createStat(agentsCount, `Agent${agentsCount !== 1 ? 's' : ''}`));
    }

    // Categories
    const categories = document.createElement('div');
    categories.className = 'plugin-categories';
    plugin.categories.forEach(cat => {
        const tag = document.createElement('span');
        tag.className = 'category-tag';
        tag.textContent = cat;
        categories.appendChild(tag);
    });

    // Footer
    const footer = document.createElement('div');
    footer.className = 'plugin-footer';

    const version = document.createElement('span');
    version.className = 'plugin-version';
    version.textContent = `v${plugin.version}`;

    const exploreBtn = document.createElement('div');
    exploreBtn.className = 'explore-btn';
    exploreBtn.innerHTML = `
        <span>Explore</span>
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path d="M6 12L10 8L6 4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
    `;

    footer.appendChild(version);
    footer.appendChild(exploreBtn);

    // Assemble card
    card.appendChild(header);
    card.appendChild(description);
    card.appendChild(stats);
    card.appendChild(categories);
    card.appendChild(footer);

    return card;
}

function createStat(value, label) {
    const stat = document.createElement('div');
    stat.className = 'stat';

    const statValue = document.createElement('div');
    statValue.className = 'stat-value';
    statValue.textContent = value;

    const statLabel = document.createElement('div');
    statLabel.className = 'stat-label';
    statLabel.textContent = label;

    stat.appendChild(statValue);
    stat.appendChild(statLabel);

    return stat;
}

function filterPlugins() {
    if (!pluginsData || !pluginsData.plugins) return [];

    return pluginsData.plugins.filter(plugin => {
        // Apply search filter
        if (searchQuery) {
            const searchableText = [
                plugin.name,
                plugin.description,
                plugin.tagline,
                ...(plugin.components.commands?.map(c => c.name) || []),
                ...(plugin.components.skills?.map(s => s.name) || []),
                ...(plugin.components.agents?.map(a => a.name) || [])
            ].join(' ').toLowerCase();

            if (!searchableText.includes(searchQuery)) {
                return false;
            }
        }

        // Apply component type filter
        if (currentFilter === 'all') return true;
        if (currentFilter === 'commands') {
            return plugin.components.commands && plugin.components.commands.length > 0;
        }
        if (currentFilter === 'skills') {
            return plugin.components.skills && plugin.components.skills.length > 0;
        }
        if (currentFilter === 'agents') {
            return plugin.components.agents && plugin.components.agents.length > 0;
        }

        return true;
    });
}

function updateCounts() {
    if (!pluginsData) return;

    let totalCommands = 0;
    let totalSkills = 0;
    let totalAgents = 0;

    pluginsData.plugins.forEach(plugin => {
        totalCommands += plugin.components.commands?.length || 0;
        totalSkills += plugin.components.skills?.length || 0;
        totalAgents += plugin.components.agents?.length || 0;
    });

    const totalComponents = totalCommands + totalSkills + totalAgents;

    const countAll = document.getElementById('countAll');
    const countCommands = document.getElementById('countCommands');
    const countSkills = document.getElementById('countSkills');

    if (countAll) countAll.textContent = totalComponents;
    if (countCommands) countCommands.textContent = totalCommands;
    if (countSkills) countSkills.textContent = totalSkills;
}

// ============================================
// Modal Functions
// ============================================
function openPluginModal(pluginId) {
    const plugin = pluginsData.plugins.find(p => p.id === pluginId);
    if (!plugin) return;

    const modal = document.getElementById('pluginModal');
    const modalBody = document.getElementById('modalBody');

    // Clear existing content
    modalBody.innerHTML = '';

    // Create modal content
    modalBody.appendChild(createModalHeader(plugin));
    modalBody.appendChild(createModalDescription(plugin));
    modalBody.appendChild(createInstallSection(plugin));

    if (plugin.requirements) {
        modalBody.appendChild(createRequirementsSection(plugin.requirements));
    }

    if (plugin.components.commands?.length > 0) {
        modalBody.appendChild(createComponentsSection('Commands', plugin.components.commands, 'command'));
    }

    if (plugin.components.skills?.length > 0) {
        modalBody.appendChild(createComponentsSection('Skills', plugin.components.skills, 'skill'));
    }

    if (plugin.components.agents?.length > 0) {
        modalBody.appendChild(createComponentsSection('Agents', plugin.components.agents, 'agent'));
    }

    modal.classList.add('active');
    document.body.style.overflow = 'hidden';
}

function createModalHeader(plugin) {
    const header = document.createElement('div');
    header.className = 'modal-header';

    const icon = document.createElement('div');
    icon.className = 'modal-icon';
    icon.textContent = plugin.icon;

    const content = document.createElement('div');
    content.className = 'modal-header-content';

    const title = document.createElement('h2');
    title.className = 'modal-title';
    title.textContent = plugin.name;

    const tagline = document.createElement('p');
    tagline.className = 'modal-tagline';
    tagline.textContent = plugin.tagline;

    const meta = document.createElement('div');
    meta.className = 'modal-meta';

    const version = document.createElement('span');
    version.className = 'plugin-version';
    version.textContent = `v${plugin.version}`;

    const author = document.createElement('span');
    author.style.color = 'var(--color-text-muted)';
    author.textContent = `by ${plugin.author}`;

    meta.appendChild(version);
    meta.appendChild(author);

    content.appendChild(title);
    content.appendChild(tagline);
    content.appendChild(meta);

    header.appendChild(icon);
    header.appendChild(content);

    return header;
}

function createModalDescription(plugin) {
    const description = document.createElement('p');
    description.className = 'modal-description';
    description.textContent = plugin.description;
    return description;
}

function createInstallSection(plugin) {
    const section = document.createElement('div');
    section.className = 'install-section';

    const title = document.createElement('div');
    title.className = 'install-title';
    title.textContent = 'Installation';

    const codeContainer = document.createElement('div');
    codeContainer.className = 'install-code';

    const code = document.createElement('code');
    code.className = 'install-command';
    code.textContent = plugin.installation;

    const copyBtn = document.createElement('button');
    copyBtn.className = 'copy-btn';
    copyBtn.innerHTML = `
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path d="M10.6667 2.66667H4.53333C3.68667 2.66667 3 3.35333 3 4.2V11.3333C3 11.7015 3.29848 12 3.66667 12C4.03486 12 4.33333 11.7015 4.33333 11.3333V4.2H10.6667C11.0349 4.2 11.3333 3.90152 11.3333 3.53333C11.3333 3.16514 11.0349 2.66667 10.6667 2.66667Z" fill="currentColor"/>
            <path d="M12 5.33333H7.33333C6.48657 5.33333 5.8 6.02 5.8 6.86667V12C5.8 12.8467 6.48657 13.5333 7.33333 13.5333H12C12.8467 13.5333 13.5333 12.8467 13.5333 12V6.86667C13.5333 6.02 12.8467 5.33333 12 5.33333Z" fill="currentColor"/>
        </svg>
    `;
    copyBtn.onclick = (e) => {
        e.stopPropagation();
        copyToClipboard(plugin.installation, copyBtn);
    };

    codeContainer.appendChild(code);
    codeContainer.appendChild(copyBtn);

    section.appendChild(title);
    section.appendChild(codeContainer);

    return section;
}

function createRequirementsSection(requirements) {
    const section = document.createElement('div');
    section.className = 'requirements-section';

    const title = document.createElement('div');
    title.className = 'requirements-title';
    title.innerHTML = `
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path d="M8 1.33334L10.06 5.50668L14.6667 6.18001L11.3333 9.42668L12.12 14.0133L8 11.8467L3.88 14.0133L4.66667 9.42668L1.33334 6.18001L5.94 5.50668L8 1.33334Z" fill="currentColor"/>
        </svg>
        Requirements
    `;

    const list = document.createElement('ul');
    list.className = 'requirements-list';

    requirements.forEach(req => {
        const item = document.createElement('li');
        item.textContent = req;
        list.appendChild(item);
    });

    section.appendChild(title);
    section.appendChild(list);

    return section;
}

function createComponentsSection(sectionTitle, components, type) {
    const section = document.createElement('div');
    section.className = 'components-section';

    const title = document.createElement('h3');
    title.className = 'section-title';
    title.textContent = sectionTitle;

    section.appendChild(title);

    components.forEach(component => {
        section.appendChild(createComponentCard(component, type));
    });

    return section;
}

function createComponentCard(component, type) {
    const card = document.createElement('div');
    card.className = 'component-card';

    // Header
    const header = document.createElement('div');
    header.className = 'component-header';

    const name = document.createElement('div');
    name.className = 'component-name';
    name.textContent = component.fullName || component.name;

    const typeLabel = document.createElement('div');
    typeLabel.className = 'component-type';
    typeLabel.textContent = type.toUpperCase();

    header.appendChild(name);
    header.appendChild(typeLabel);

    // Description
    const description = document.createElement('p');
    description.className = 'component-description';
    description.textContent = component.description;

    // Usage
    const usage = document.createElement('div');
    usage.className = 'component-usage';

    const usageLabel = document.createElement('div');
    usageLabel.className = 'usage-label';
    usageLabel.textContent = 'Usage';

    const usageText = document.createElement('div');
    usageText.className = 'usage-text';
    usageText.textContent = component.usage;

    usage.appendChild(usageLabel);
    usage.appendChild(usageText);

    card.appendChild(header);
    card.appendChild(description);
    card.appendChild(usage);

    // Features (for skills)
    if (component.features) {
        const featuresDiv = document.createElement('div');
        featuresDiv.className = 'component-features';

        const featuresTitle = document.createElement('div');
        featuresTitle.className = 'features-title';
        featuresTitle.textContent = 'Features';

        const featuresList = document.createElement('ul');
        featuresList.className = 'features-list';

        component.features.forEach(feature => {
            const item = document.createElement('li');
            item.textContent = feature;
            featuresList.appendChild(item);
        });

        featuresDiv.appendChild(featuresTitle);
        featuresDiv.appendChild(featuresList);
        card.appendChild(featuresDiv);
    }

    // Example
    if (component.example) {
        const example = document.createElement('div');
        example.className = 'component-example';
        example.textContent = component.example;
        card.appendChild(example);
    }

    // Examples (multiple)
    if (component.examples) {
        const examplesDiv = document.createElement('div');
        examplesDiv.className = 'component-examples';

        const examplesTitle = document.createElement('div');
        examplesTitle.className = 'features-title';
        examplesTitle.textContent = 'Examples';

        const examplesList = document.createElement('ul');
        examplesList.className = 'examples-list';

        component.examples.forEach(ex => {
            const item = document.createElement('li');
            item.textContent = ex;
            examplesList.appendChild(item);
        });

        examplesDiv.appendChild(examplesTitle);
        examplesDiv.appendChild(examplesList);
        card.appendChild(examplesDiv);
    }

    return card;
}

function closeModal() {
    const modal = document.getElementById('pluginModal');
    modal.classList.remove('active');
    document.body.style.overflow = '';
}

// ============================================
// Utility Functions
// ============================================
async function copyToClipboard(text, button) {
    try {
        await navigator.clipboard.writeText(text);

        // Visual feedback
        const originalHTML = button.innerHTML;
        button.classList.add('copied');
        button.innerHTML = `
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                <path d="M13.3333 4L6 11.3333L2.66667 8" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
        `;

        setTimeout(() => {
            button.classList.remove('copied');
            button.innerHTML = originalHTML;
        }, 2000);
    } catch (err) {
        console.error('Failed to copy:', err);
    }
}

function scrollToPlugins() {
    const marketplace = document.getElementById('marketplace');
    if (marketplace) {
        marketplace.scrollIntoView({ behavior: 'smooth' });
    }
}

function copyInstallCommand() {
    const command = '/plugin marketplace add simonlee2/claude-plugins';
    copyToClipboardWithFeedback(command);
}

async function copyToClipboardWithFeedback(text) {
    try {
        await navigator.clipboard.writeText(text);

        // Create temporary toast notification
        const toast = document.createElement('div');
        toast.style.cssText = `
            position: fixed;
            bottom: 2rem;
            right: 2rem;
            background: var(--color-success);
            color: var(--color-bg-primary);
            padding: 1rem 1.5rem;
            border-radius: var(--radius-md);
            font-family: var(--font-code);
            font-size: 0.875rem;
            font-weight: 500;
            z-index: 10000;
            box-shadow: var(--shadow-lg);
            animation: slideInUp 0.3s ease;
        `;
        toast.textContent = '✓ Copied to clipboard!';
        document.body.appendChild(toast);

        setTimeout(() => {
            toast.style.animation = 'fadeOut 0.3s ease';
            setTimeout(() => toast.remove(), 300);
        }, 2000);
    } catch (err) {
        console.error('Failed to copy:', err);
    }
}

// ============================================
// Export functions for inline onclick handlers
// ============================================
window.openPluginModal = openPluginModal;
window.closeModal = closeModal;
window.copyToClipboard = copyToClipboard;
window.scrollToPlugins = scrollToPlugins;
window.copyInstallCommand = copyInstallCommand;

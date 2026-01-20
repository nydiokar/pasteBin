/**
 * Paste Server Frontend - Functional, clean, no classes
 * ChatGPT-style interface with infinite loading
 */

// ============================================================================
// State Management - Simple, explicit
// ============================================================================

const state = {
    authenticated: false,
    pastes: [],
    selectedPasteId: null,
    offset: 0,
    limit: 50,
    totalPastes: 0,
    loading: false,
    hasMore: true,
    searchQuery: '',
};

// ============================================================================
// API Layer - Pure functions returning promises
// ============================================================================

const api = {
    async login(password) {
        const response = await fetch('/api/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ password }),
            credentials: 'include',
        });
        if (!response.ok) throw new Error('Invalid password');
        return response.json();
    },

    async logout() {
        const response = await fetch('/api/logout', {
            method: 'POST',
            credentials: 'include',
        });
        return response.json();
    },

    async getPastes(limit = 50, offset = 0) {
        const response = await fetch(
            `/api/pastes?limit=${limit}&offset=${offset}`,
            { credentials: 'include' }
        );
        if (!response.ok) throw new Error('Failed to fetch pastes');
        return response.json();
    },

    async createPaste(content) {
        const response = await fetch('/api/paste', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ content }),
            credentials: 'include',
        });
        if (!response.ok) throw new Error('Failed to create paste');
        return response.json();
    },

    async deletePaste(pasteId) {
        const response = await fetch(`/api/paste/${pasteId}`, {
            method: 'DELETE',
            credentials: 'include',
        });
        if (!response.ok) throw new Error('Failed to delete paste');
        return response.json();
    },
};

// ============================================================================
// Date Utilities
// ============================================================================

function formatTimestamp(isoString) {
    const date = new Date(isoString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;

    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

function getDateGroup(isoString) {
    const date = new Date(isoString);
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);
    const pasteDate = new Date(date.getFullYear(), date.getMonth(), date.getDate());

    if (pasteDate.getTime() === today.getTime()) return 'Today';
    if (pasteDate.getTime() === yesterday.getTime()) return 'Yesterday';

    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

function groupPastesByDate(pastes) {
    const groups = {};
    pastes.forEach(paste => {
        const group = getDateGroup(paste.created_at);
        if (!groups[group]) groups[group] = [];
        groups[group].push(paste);
    });
    return groups;
}

// ============================================================================
// Theme Management
// ============================================================================

function getTheme() {
    return localStorage.getItem('theme') || 'light';
}

function setTheme(theme) {
    document.body.dataset.theme = theme;
    localStorage.setItem('theme', theme);
    updateThemeIcon(theme);
}

function toggleTheme() {
    const currentTheme = getTheme();
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    setTheme(newTheme);
}

function updateThemeIcon(theme) {
    const icon = document.getElementById('theme-toggle');
    icon.textContent = theme === 'light' ? '🌙' : '☀️';
}

// ============================================================================
// UI Rendering
// ============================================================================

function renderSidebar(pastes, searchQuery = '') {
    const sidebarContent = document.getElementById('sidebar-content');

    // Filter pastes by search query
    const filteredPastes = searchQuery
        ? pastes.filter(p =>
              p.content.toLowerCase().includes(searchQuery.toLowerCase())
          )
        : pastes;

    if (filteredPastes.length === 0) {
        sidebarContent.innerHTML = '<div class="loading">No pastes found</div>';
        return;
    }

    // Group by date
    const groups = groupPastesByDate(filteredPastes);

    let html = '';
    Object.entries(groups).forEach(([groupName, groupPastes]) => {
        html += `
            <div class="date-group">
                <div class="date-group-header" onclick="toggleGroup(this)">
                    <span>${groupName}</span>
                    <span class="collapse-icon">▼</span>
                </div>
                <ul class="paste-list">
                    ${groupPastes
                        .map(
                            paste => `
                        <li class="paste-item ${
                            paste.id === state.selectedPasteId ? 'active' : ''
                        }"
                            data-paste-id="${paste.id}"
                            onclick="selectPaste(${paste.id})">
                            <div class="paste-time">${formatTimestamp(paste.created_at)}</div>
                            <div class="paste-preview">${truncateText(paste.content, 50)}</div>
                        </li>
                    `
                        )
                        .join('')}
                </ul>
            </div>
        `;
    });

    sidebarContent.innerHTML = html;

    // Setup infinite scroll
    setupInfiniteScroll();
}

function renderMainArea(pasteId) {
    const mainContent = document.getElementById('main-content');

    // Get the selected paste and the 2 pastes after it (last 3 total)
    const selectedIndex = state.pastes.findIndex(p => p.id === pasteId);

    if (selectedIndex === -1) {
        mainContent.innerHTML = '<div class="empty-state"><p>Paste not found</p></div>';
        return;
    }

    // Get up to 3 pastes starting from selected one
    const pastesToShow = state.pastes.slice(selectedIndex, selectedIndex + 3);

    const pastesHtml = pastesToShow.map(paste => {
        const fullTimestamp = new Date(paste.created_at).toLocaleString('en-US', {
            month: 'short',
            day: 'numeric',
            year: 'numeric',
            hour: 'numeric',
            minute: '2-digit',
            hour12: true,
        });

        return `
            <div class="paste-card">
                <div class="paste-header">
                    <span class="paste-timestamp">${fullTimestamp}</span>
                    <div class="paste-actions">
                        <button class="secondary-btn btn-small" onclick="copyPaste(${paste.id}, event)">
                            📋 Copy
                        </button>
                        <button class="danger-btn btn-small" onclick="showDeleteModal(${paste.id})">
                            🗑️ Delete
                        </button>
                    </div>
                </div>
                <div class="paste-content">${escapeHtml(paste.content)}</div>
            </div>
        `;
    }).join('');

    mainContent.innerHTML = `
        <div class="paste-display">
            ${pastesHtml}
        </div>
    `;
}

// ============================================================================
// User Actions
// ============================================================================

async function handleLogin(event) {
    event.preventDefault();
    const password = document.getElementById('password-input').value;
    const errorEl = document.getElementById('login-error');

    try {
        await api.login(password);
        state.authenticated = true;
        showApp();
        await loadPastes();
    } catch (err) {
        errorEl.textContent = err.message;
        errorEl.classList.remove('hidden');
    }
}

async function handleLogout() {
    try {
        await api.logout();
        state.authenticated = false;
        state.pastes = [];
        state.selectedPasteId = null;
        state.offset = 0;
        showLogin();
    } catch (err) {
        console.error('Logout failed:', err);
    }
}

async function loadPastes(append = false) {
    if (state.loading || (!append && state.pastes.length > 0)) return;

    state.loading = true;

    try {
        const data = await api.getPastes(state.limit, state.offset);

        if (append) {
            state.pastes = [...state.pastes, ...data.pastes];
        } else {
            state.pastes = data.pastes;
        }

        state.totalPastes = data.total;
        state.offset += data.pastes.length;
        state.hasMore = state.offset < state.totalPastes;

        renderSidebar(state.pastes, state.searchQuery);

        // Auto-select latest paste on initial load
        if (!state.selectedPasteId && state.pastes.length > 0) {
            selectPaste(state.pastes[0].id);
        } else if (state.selectedPasteId) {
            renderMainArea(state.selectedPasteId);
        }
    } catch (err) {
        console.error('Failed to load pastes:', err);
    } finally {
        state.loading = false;
    }
}

async function refreshPastes() {
    if (state.loading) return;

    const refreshBtn = document.getElementById('refresh-btn');
    refreshBtn.innerHTML = '⏳';
    refreshBtn.disabled = true;

    try {
        // Reset state to reload from beginning
        state.offset = 0;
        state.hasMore = true;
        state.pastes = [];

        const data = await api.getPastes(state.limit, 0);

        state.pastes = data.pastes;
        state.totalPastes = data.total;
        state.offset = data.pastes.length;
        state.hasMore = state.offset < state.totalPastes;

        renderSidebar(state.pastes, state.searchQuery);

        // Re-select current paste if it still exists, otherwise select latest
        const currentPasteExists = state.pastes.find(p => p.id === state.selectedPasteId);
        if (currentPasteExists) {
            renderMainArea(state.selectedPasteId);
        } else if (state.pastes.length > 0) {
            selectPaste(state.pastes[0].id);
        }

        // Visual feedback
        refreshBtn.innerHTML = '✓';
        setTimeout(() => {
            refreshBtn.innerHTML = '🔄';
        }, 1000);
    } catch (err) {
        console.error('Failed to refresh pastes:', err);
        refreshBtn.innerHTML = '✗';
        setTimeout(() => {
            refreshBtn.innerHTML = '🔄';
        }, 2000);
    } finally {
        refreshBtn.disabled = false;
    }
}

async function handleCreatePaste() {
    const textarea = document.getElementById('new-paste-textarea');
    const content = textarea.value.trim();

    if (!content) return;

    try {
        const newPaste = await api.createPaste(content);

        // Add to state at the beginning
        state.pastes.unshift({
            id: newPaste.id,
            content: content,
            created_at: newPaste.created_at,
        });

        // Re-render sidebar
        renderSidebar(state.pastes, state.searchQuery);

        // Select the new paste
        selectPaste(newPaste.id);

        // Close modal and clear textarea
        hideNewPasteModal();
        textarea.value = '';
    } catch (err) {
        console.error('Failed to create paste:', err);
        alert('Failed to create paste. Please try again.');
    }
}

async function handleDeletePaste(pasteId) {
    try {
        await api.deletePaste(pasteId);

        // Remove from state
        state.pastes = state.pastes.filter(p => p.id !== pasteId);

        // Re-render sidebar
        renderSidebar(state.pastes, state.searchQuery);

        // Select next paste or show empty state
        if (state.pastes.length > 0) {
            selectPaste(state.pastes[0].id);
        } else {
            document.getElementById('main-content').innerHTML =
                '<div class="empty-state"><p>No pastes yet. Click "+ New Dump" to create one.</p></div>';
            state.selectedPasteId = null;
        }

        hideDeleteModal();
    } catch (err) {
        console.error('Failed to delete paste:', err);
        alert('Failed to delete paste. Please try again.');
    }
}

function selectPaste(pasteId) {
    state.selectedPasteId = pasteId;

    // Update sidebar active state
    document.querySelectorAll('.paste-item').forEach(item => {
        item.classList.toggle('active', item.dataset.pasteId == pasteId);
    });

    // Render in main area
    renderMainArea(pasteId);
}

function copyPaste(pasteId, event) {
    const paste = state.pastes.find(p => p.id === pasteId);
    if (!paste) return;

    const btn = event.target.closest('button');
    const originalText = btn.innerHTML;

    // Try modern clipboard API first
    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(paste.content)
            .then(() => {
                btn.innerHTML = '✓ Copied';
                setTimeout(() => {
                    btn.innerHTML = originalText;
                }, 1500);
            })
            .catch(() => {
                // Fallback if clipboard API fails
                fallbackCopy(paste.content, btn, originalText);
            });
    } else {
        // Use fallback for HTTP or older browsers
        fallbackCopy(paste.content, btn, originalText);
    }
}

function fallbackCopy(text, btn, originalText) {
    // Create temporary textarea
    const textarea = document.createElement('textarea');
    textarea.value = text;
    textarea.style.position = 'fixed';
    textarea.style.top = '0';
    textarea.style.left = '0';
    textarea.style.opacity = '0';
    document.body.appendChild(textarea);

    // Select and copy
    textarea.focus();
    textarea.select();

    try {
        const successful = document.execCommand('copy');
        if (successful) {
            btn.innerHTML = '✓ Copied';
            setTimeout(() => {
                btn.innerHTML = originalText;
            }, 1500);
        } else {
            btn.innerHTML = '✗ Failed';
            setTimeout(() => {
                btn.innerHTML = originalText;
            }, 2000);
        }
    } catch (err) {
        console.error('Copy failed:', err);
        btn.innerHTML = '✗ Failed';
        setTimeout(() => {
            btn.innerHTML = originalText;
        }, 2000);
    } finally {
        document.body.removeChild(textarea);
    }
}

function handleSearch(event) {
    state.searchQuery = event.target.value;
    renderSidebar(state.pastes, state.searchQuery);
}

// ============================================================================
// Modal Management
// ============================================================================

function showNewPasteModal() {
    document.getElementById('new-paste-modal').classList.remove('hidden');
    document.getElementById('new-paste-textarea').focus();
}

function hideNewPasteModal() {
    document.getElementById('new-paste-modal').classList.add('hidden');
    document.getElementById('new-paste-textarea').value = '';
}

let pasteToDelete = null;

function showDeleteModal(pasteId) {
    pasteToDelete = pasteId;
    document.getElementById('delete-modal').classList.remove('hidden');
}

function hideDeleteModal() {
    pasteToDelete = null;
    document.getElementById('delete-modal').classList.add('hidden');
}

// ============================================================================
// UI Utilities
// ============================================================================

function showLogin() {
    document.getElementById('login-screen').classList.remove('hidden');
    document.getElementById('app').classList.add('hidden');
}

function showApp() {
    document.getElementById('login-screen').classList.add('hidden');
    document.getElementById('app').classList.remove('hidden');
}

function toggleSidebar() {
    document.getElementById('sidebar').classList.toggle('open');
}

function toggleGroup(headerEl) {
    headerEl.closest('.date-group').classList.toggle('collapsed');
}

function truncateText(text, maxLength) {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function setupInfiniteScroll() {
    const sidebarContent = document.getElementById('sidebar-content');

    const observer = new IntersectionObserver(
        entries => {
            entries.forEach(entry => {
                if (entry.isIntersecting && state.hasMore && !state.loading) {
                    loadPastes(true);
                }
            });
        },
        { threshold: 1.0 }
    );

    // Observe the last paste item
    const lastGroup = sidebarContent.querySelector('.date-group:last-child');
    if (lastGroup) {
        const lastItem = lastGroup.querySelector('.paste-item:last-child');
        if (lastItem) observer.observe(lastItem);
    }
}

// ============================================================================
// Event Listeners Setup
// ============================================================================

function setupEventListeners() {
    // Login
    document.getElementById('login-form').addEventListener('submit', handleLogin);

    // Logout
    document.getElementById('logout-btn').addEventListener('click', handleLogout);

    // Refresh
    document.getElementById('refresh-btn').addEventListener('click', refreshPastes);

    // Theme toggle
    document.getElementById('theme-toggle').addEventListener('click', toggleTheme);

    // New paste modal
    document.getElementById('new-paste-btn').addEventListener('click', showNewPasteModal);
    document.querySelector('#new-paste-modal .modal-close').addEventListener('click', hideNewPasteModal);
    document.querySelector('#new-paste-modal .modal-overlay').addEventListener('click', hideNewPasteModal);
    document.getElementById('cancel-paste-btn').addEventListener('click', hideNewPasteModal);
    document.getElementById('save-paste-btn').addEventListener('click', handleCreatePaste);

    // Delete modal
    document.querySelector('#delete-modal .modal-overlay').addEventListener('click', hideDeleteModal);
    document.getElementById('cancel-delete-btn').addEventListener('click', hideDeleteModal);
    document.getElementById('confirm-delete-btn').addEventListener('click', () => {
        if (pasteToDelete) handleDeletePaste(pasteToDelete);
    });

    // Search
    document.getElementById('search-input').addEventListener('input', handleSearch);

    // Sidebar toggle (mobile)
    document.getElementById('sidebar-toggle').addEventListener('click', toggleSidebar);

    // Keyboard shortcuts
    document.addEventListener('keydown', event => {
        // Ctrl/Cmd + N: New paste
        if ((event.ctrlKey || event.metaKey) && event.key === 'n') {
            event.preventDefault();
            showNewPasteModal();
        }

        // Escape: Close modals
        if (event.key === 'Escape') {
            hideNewPasteModal();
            hideDeleteModal();
        }

        // Ctrl/Cmd + Enter: Save paste (when modal is open)
        if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
            const modal = document.getElementById('new-paste-modal');
            if (!modal.classList.contains('hidden')) {
                event.preventDefault();
                handleCreatePaste();
            }
        }
    });
}

// ============================================================================
// Initialization
// ============================================================================

async function checkAuth() {
    try {
        // Try to fetch pastes - if successful, user is logged in
        const response = await fetch('/api/pastes?limit=1&offset=0', {
            credentials: 'include'
        });

        if (response.ok) {
            state.authenticated = true;
            showApp();
            await loadPastes();
        } else {
            showLogin();
        }
    } catch (err) {
        showLogin();
    }
}

async function init() {
    // Apply saved theme
    setTheme(getTheme());

    // Setup event listeners
    setupEventListeners();

    // Check if already authenticated
    await checkAuth();
}

// Start the app
document.addEventListener('DOMContentLoaded', init);

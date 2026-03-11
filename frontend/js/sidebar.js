// frontend/js/sidebar.js
// Sidebar reutilizável — incluir em todas as páginas autenticadas

function initSidebar(activePage) {
    const user = JSON.parse(localStorage.getItem('user') || '{}');

    // Guard — só redireciona se não estivermos na login
    if (!localStorage.getItem('access_token')) {
        window.location.href = 'login.html';
        return;
    }

    const isPrivileged = user.role === 'chefe' || user.role === 'admin';
    const initial = (user.username || '?')[0].toUpperCase();

    const roleLabels = { staff: 'Staff', chefe: 'Chefe', admin: 'Admin' };
    const roleColors = { staff: 'badge-blue', chefe: 'badge-purple', admin: 'badge-red' };

    const navItems = [
        { id: 'dashboard',  icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/></svg>`, label: 'Dashboard',  href: 'dashboard.html' },
        { id: 'inbox',      icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>`, label: 'Inbox', href: 'inbox.html', badge: true },
        { id: 'gestao',     icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>`, label: 'Gestões',    href: 'gestao.html' },
        { id: 'hierarquia', icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>`, label: 'Hierarquia', href: 'hierarquia.html', restricted: true },
    ];

    const visibleItems = navItems.filter(i => !i.restricted || isPrivileged);

    const navHTML = visibleItems.map(item => `
        <a href="${item.href}" class="nav-link${activePage === item.id ? ' active' : ''}">
            <span class="nav-icon">${item.icon}</span>
            <span>${item.label}</span>
            ${item.badge ? `<span class="nav-badge" id="nav-badge-inbox" style="display:none">0</span>` : ''}
        </a>`).join('');

    const el = document.getElementById('sidebar');
    if (!el) return;

    el.innerHTML = `
        <div class="sidebar-logo">
            <div class="logo-text">KALLI<span>RP</span></div>
            <div class="logo-sub">Staff Panel</div>
        </div>
        <nav class="sidebar-nav">
            <p class="nav-section-label">Menu</p>
            ${navHTML}
        </nav>
        <div class="sidebar-footer">
            <div class="sidebar-avatar">${initial}</div>
            <div class="sidebar-user-info">
                <div class="sidebar-username">${user.username || '—'}</div>
                <span class="badge ${roleColors[user.role] || 'badge-blue'}" style="font-size:.6rem">${roleLabels[user.role] || user.role}</span>
            </div>
            <button class="btn-logout" title="Terminar sessão" onclick="logout()">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>
            </button>
        </div>`;

    // Atualizar badge do inbox
    _loadInboxBadge();
}

async function _loadInboxBadge() {
    try {
        const data = await Inbox.countNaoLidas();
        if (data.count > 0) {
            const badge = document.getElementById('nav-badge-inbox');
            if (badge) { badge.textContent = data.count; badge.style.display = 'inline-flex'; }
        }
    } catch (_) {}
}

// Expor para que inbox.html possa chamar após marcar como lida
function loadInboxBadge() { _loadInboxBadge(); }

function logout() {
    localStorage.clear();
    window.location.href = 'login.html';
}

// ── Toast notifications ───────────────────────────────────────
function showToast(msg, type = 'info') {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container';
        document.body.appendChild(container);
    }
    const icons = { success: '✓', error: '✕', info: 'ℹ' };
    const el = document.createElement('div');
    el.className = `toast ${type}`;
    el.innerHTML = `<span class="toast-icon">${icons[type] || 'ℹ'}</span><span>${msg}</span>`;
    container.appendChild(el);
    setTimeout(() => { el.style.opacity = '0'; setTimeout(() => el.remove(), 300); }, 3200);
}

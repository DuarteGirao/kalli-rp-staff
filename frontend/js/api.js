// frontend/js/api.js
const API_BASE = 'http://localhost:8000';
 
// Guardar tokens no localStorage
function getAccessToken()  { return localStorage.getItem('access_token'); }
function getRefreshToken() { return localStorage.getItem('refresh_token'); }
 
function saveTokens(access, refresh) {
    localStorage.setItem('access_token', access);
    localStorage.setItem('refresh_token', refresh);
}
 
// Tentar renovar o access token quando expira
async function refreshAccessToken() {
    const refresh = getRefreshToken();
    if (!refresh) { window.location.href = '/pages/login.html'; return null; }
    const res = await fetch(`${API_BASE}/auth/refresh`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: refresh })
    });
    if (!res.ok) { window.location.href = '/pages/login.html'; return null; }
    const data = await res.json();
    saveTokens(data.access_token, data.refresh_token);
    return data.access_token;
}
 
// Função principal para fazer chamadas autenticadas
async function apiFetch(path, options = {}) {
    let token = getAccessToken();
    const headers = {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
        ...options.headers
    };
    let res = await fetch(`${API_BASE}${path}`, { ...options, headers });
 
    // Se o token expirou (401), tenta renovar e repetir
    if (res.status === 401) {
        token = await refreshAccessToken();
        if (!token) return null;
        headers['Authorization'] = `Bearer ${token}`;
        res = await fetch(`${API_BASE}${path}`, { ...options, headers });
    }
    if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Erro desconhecido');
    }
    return res.json();
}
 
// Funções específicas por módulo
const Auth    = { login: (u,p) => fetch(`${API_BASE}/auth/login`,
    { method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({username:u, password:p}) }).then(r=>r.json()) };
 
const Inbox   = {
    get:         ()    => apiFetch('/inbox/'),
    countNaoLidas: ()  => apiFetch('/inbox/nao-lidas/count'),
    marcarLida:  (id)  => apiFetch(`/inbox/${id}/lida`, { method:'PATCH' })
};
 
const Reports = {
    myStats:   ()     => apiFetch('/reports/stats/me'),
    importCSV: (form) => apiFetch('/reports/import', { method:'POST', body:form,
        headers:{ 'Authorization': `Bearer ${getAccessToken()}` } })
};

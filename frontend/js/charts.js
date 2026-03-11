// frontend/js/charts.js
// -- Dark theme global defaults (applied once when Chart.js loads) --
if (typeof Chart !== 'undefined') {
    Chart.defaults.color          = '#8484a0';
    Chart.defaults.borderColor    = '#272736';
    Chart.defaults.font.family    = "'Inter', system-ui, sans-serif";
    Chart.defaults.font.size      = 12;
}

let myChart = null;
let chartData = null;
 
async function loadDashboard() {
    const stats = await Reports.myStats();
 
    // Atualizar cards de estatísticas
    document.getElementById('stat-reports').textContent = stats.reports;
    document.getElementById('stat-tickets').textContent = stats.tickets;
 
    chartData = stats;
    renderDonut(stats.reports, stats.tickets);
}
 
function renderDonut(reports, tickets) {
    const ctx = document.getElementById('myChart').getContext('2d');
    if (myChart) myChart.destroy();
    myChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Reports', 'Tickets'],
            datasets: [{
                data: [reports, tickets],
                backgroundColor: ['rgba(124,58,237,.85)', 'rgba(59,130,246,.85)'],
                borderColor:     ['#7c3aed', '#3b82f6'],
                borderWidth: 2,
                hoverOffset: 6
            }]
        },
        options: {
            responsive: true,
            cutout: '65%',
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { padding: 20, usePointStyle: true, pointStyleWidth: 10 }
                },
                tooltip: { callbacks: {
                    label: ctx => ` ${ctx.label}: ${ctx.parsed}`
                }}
            }
        }
    });
}
 
function renderLine(historico) {
    // Agrupar por período
    const periodos = [...new Set(historico.map(h => h.periodo))].sort();
    const repData  = periodos.map(p => {
        const h = historico.find(x => x.periodo === p && x.tipo === 'report');
        return h ? h.total : 0;
    });
    const tikData  = periodos.map(p => {
        const h = historico.find(x => x.periodo === p && x.tipo === 'ticket');
        return h ? h.total : 0;
    });
 
    const ctx = document.getElementById('myChart').getContext('2d');
    if (myChart) myChart.destroy();
    myChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: periodos,
            datasets: [
                { label: 'Reports', data: repData,
                  borderColor: '#7c3aed',
                  backgroundColor: 'rgba(124,58,237,.12)',
                  tension: 0.4, fill: true, pointRadius: 4,
                  pointBackgroundColor: '#7c3aed' },
                { label: 'Tickets', data: tikData,
                  borderColor: '#3b82f6',
                  backgroundColor: 'rgba(59,130,246,.12)',
                  tension: 0.4, fill: true, pointRadius: 4,
                  pointBackgroundColor: '#3b82f6' }
            ]
        },
        options: {
            responsive: true,
            interaction: { mode: 'index', intersect: false },
            scales: {
                x: { grid: { color: '#272736' }, ticks: { color: '#8484a0' } },
                y: { beginAtZero: true, grid: { color: '#272736' }, ticks: { color: '#8484a0' } }
            }
        }
    });
}
 
function toggleChart(tipo) {
    document.getElementById('btn-donut').classList.toggle('active', tipo==='donut');
    document.getElementById('btn-line').classList.toggle('active', tipo==='line');
    if (!chartData) return;
    if (tipo === 'donut') renderDonut(chartData?.reports || 0, chartData?.tickets || 0);
    else renderLine(chartData?.historico || []);
}

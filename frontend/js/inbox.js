// frontend/js/inbox.js
 
async function checkInbox() {
    try {
        const data = await Inbox.countNaoLidas();
        if (data.count > 0) {
            document.getElementById('popup-count').textContent =
                `Tens ${data.count} mensagem(ns) não lida(s) na tua inbox.`;
            document.getElementById('popup-inbox').style.display = 'flex';
        }
    } catch (e) {
        console.error('Erro ao verificar inbox:', e);
    }
}

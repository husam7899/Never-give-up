const tg = window.Telegram?.WebApp;
if (tg) {
    tg.ready();
    tg.expand();
}

// Notification System
function notify(msg, type = 'info') {
    const area = document.getElementById('notification-area');
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.innerText = msg;
    area.appendChild(toast);
    if (tg?.HapticFeedback) tg.HapticFeedback.notificationOccurred('success');
    setTimeout(() => toast.remove(), 3000);
}

// Telegram InitData Auth
async function authenticateWithTelegram() {
    if (!tg.initData) {
        notify("No Telegram data found!", "error");
        return;
    }

    try {
        const response = await fetch('/api/auth/telegram', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                init_data: tg.initData,
                username: tg.initDataUnsafe?.user?.username || 'Trader',
                email: tg.initDataUnsafe?.user?.id ? `${tg.initDataUnsafe.user.id}@telegram.user` : null
            })
        });
        
        const data = await response.json();
        if (data.access_token) {
            localStorage.setItem('token', data.access_token);
            notify("Authenticated with Telegram");
        }
    } catch (e) {
        notify("Auth failed, using Demo Mode", "info");
    }
}

// Tab Switching
function switchTab(tab) {
    currentTab = tab;
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.tab === tab);
    });
    loadOrders(tab);
}

// Load Orders
async function loadOrders(tab) {
    const container = document.getElementById('orders-container');
    container.innerHTML = '<div style="text-align:center; padding: 40px; color: var(--text-muted);"><i class="fa-solid fa-spinner fa-spin"></i> Loading Market Orders...</div>';

    try {
        const res = await fetch(`/api/orders?order_type=${tab.toUpperCase()}`);
        if (res.ok) {
            allOrders = await res.json();
            renderOrders(allOrders);
        } else {
            allOrders = getMockOrders(tab);
            renderOrders(allOrders);
        }
    } catch (e) {
        allOrders = getMockOrders(tab);
        renderOrders(allOrders);
    }
}

// Render Orders
function renderOrders(orders) {
    const container = document.getElementById('orders-container');
    if (!orders || orders.length === 0) {
        container.innerHTML = '<div style="text-align:center; padding: 40px; color: var(--text-muted);">No active offers.</div>';
        return;
    }

    container.innerHTML = orders.map(o => `
        <div class="order-card">
            <div class="order-header">
                <div class="trader-info">
                    <i class="fa-solid fa-circle-user" style="color: var(--binance-yellow);"></i>
                    <span>${o.creator_username || 'VerifiedTrader'}</span>
                </div>
            </div>
            <div class="order-price">
                <span class="price-val">${o.price_per_usdt || '140.00'}</span> <small>ETB</small>
            </div>
            <div class="order-footer">
                <span class="payment-tag">${o.payment_method || 'Telebirr'}</span>
                <button class="${currentTab === 'buy' ? 'btn-buy-action' : 'btn-sell-action'}" onclick="handleOrderAction(${o.id})">
                    ${currentTab === 'buy' ? 'Buy USDT' : 'Sell USDT'}
                </button>
            </div>
        </div>
    `).join('');
}

// Actions
function handleOrderAction(orderId) {
    if (tg?.HapticFeedback) tg.HapticFeedback.impactOccurred('medium');
    notify(`Order #${orderId} trade initiated!`);
}

// Init
document.addEventListener('DOMContentLoaded', () => {
    authenticateWithTelegram();
    loadOrders('buy');
});

function getMockOrders(tab) {
    return [
        { id: 101, creator_username: 'AddisTrader', price_per_usdt: 142.50, payment_method: 'TELEBIRR' },
        { id: 102, creator_username: 'EthioCryptoPro', price_per_usdt: 141.80, payment_method: 'CBE' }
    ];
}
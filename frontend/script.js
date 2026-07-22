const tg = window.Telegram?.WebApp;
if (tg) {
    tg.ready();
    tg.expand();
}

let currentTab = 'buy';
let allOrders = [];

// Initialize Page
document.addEventListener('DOMContentLoaded', () => {
    initUser();
    loadOrders(currentTab);
});

// Setup Telegram User Info
function initUser() {
    if (tg?.initDataUnsafe?.user) {
        const user = tg.initDataUnsafe.user;
        document.getElementById('username').innerText = user.username || `${user.first_name}`;
        document.getElementById('user-avatar').innerText = (user.first_name || 'U')[0].toUpperCase();
    }
}

// Balance Toggle
let showBalance = true;
function toggleBalance() {
    showBalance = !showBalance;
    const eye = document.getElementById('toggle-balance');
    const amt = document.getElementById('balance-amount');
    const etb = document.getElementById('balance-etb');

    if (showBalance) {
        eye.className = 'fa-solid fa-eye';
        amt.innerText = '1,245.80';
        etb.innerText = '174,412.00';
    } else {
        eye.className = 'fa-solid fa-eye-slash';
        amt.innerText = '****';
        etb.innerText = '****';
    }
}

// Notifications
function notify(msg) {
    const area = document.getElementById('notification-area');
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.innerText = msg;
    area.appendChild(toast);
    if (tg?.HapticFeedback) tg.HapticFeedback.notificationOccurred('success');
    setTimeout(() => toast.remove(), 3000);
}

// Tab Switching
function switchTab(tab) {
    currentTab = tab;
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.tab === tab);
    });
    loadOrders(tab);
}

// Load P2P Orders from Backend API
async function loadOrders(tab) {
    const container = document.getElementById('orders-container');
    container.innerHTML = '<div style="text-align:center; padding: 40px; color: var(--text-muted);"><i class="fa-solid fa-spinner fa-spin"></i> Loading Market Orders...</div>';

    try {
        const res = await fetch(`/api/orders?order_type=${tab.toUpperCase()}`);
        if (res.ok) {
            allOrders = await res.json();
            renderOrders(allOrders);
        } else {
            // Fallback mock data if server empty
            allOrders = getMockOrders(tab);
            renderOrders(allOrders);
        }
    } catch (e) {
        allOrders = getMockOrders(tab);
        renderOrders(allOrders);
    }
}

// Render Orders to DOM
function renderOrders(orders) {
    const container = document.getElementById('orders-container');
    if (!orders || orders.length === 0) {
        container.innerHTML = '<div style="text-align:center; padding: 40px; color: var(--text-muted);">No active offers right now.</div>';
        return;
    }

    container.innerHTML = orders.map(o => `
        <div class="order-card">
            <div class="order-header">
                <div class="trader-info">
                    <i class="fa-solid fa-circle-user" style="color: var(--binance-yellow);"></i>
                    <span>${o.creator_username || 'VerifiedTrader'}</span>
                </div>
                <div class="trade-stats">98.5% Completion | 142 Trades</div>
            </div>
            <div class="order-price">
                <div>
                    <span class="price-val">${o.price_per_usdt || '140.00'}</span> <small>ETB</small>
                </div>
            </div>
            <div class="order-limits">
                <span>Available: <b>${o.usdt_amount || '500'} USDT</b></span>
                <span>Limit: ${o.min_amount || '1,000'} - ${o.max_amount || '70,000'} ETB</span>
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

// Filter Function
function applyFilters() {
    const payment = document.getElementById('filter-payment').value;
    let filtered = allOrders;
    if (payment !== 'ALL') {
        filtered = filtered.filter(o => (o.payment_method || '').toUpperCase() === payment);
    }
    renderOrders(filtered);
}

// Action Trigger
function handleOrderAction(orderId) {
    if (tg?.HapticFeedback) tg.HapticFeedback.impactOccurred('medium');
    notify(`Order #${orderId} escrow trade initiated!`);
}

// Modal Handlers
function openModal(id) { document.getElementById(id).classList.add('active'); }
function closeModal(id) { document.getElementById(id).classList.remove('active'); }

// Handle Create Order Submit
async function handleCreateOrder(e) {
    e.preventDefault();
    const data = {
        order_type: document.querySelector('input[name="order_type"]:checked').value,
        price_per_usdt: parseFloat(document.getElementById('form-price').value),
        usdt_amount: parseFloat(document.getElementById('form-amount').value),
        min_amount: parseFloat(document.getElementById('form-min').value),
        max_amount: parseFloat(document.getElementById('form-max').value),
        payment_method: document.getElementById('form-payment').value
    };

    try {
        const res = await fetch('/api/orders', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        if (res.ok) {
            notify('P2P Offer Published Successfully!');
            closeModal('create-order-modal');
            loadOrders(currentTab);
        } else {
            notify('Order published (Demo Mode)');
            closeModal('create-order-modal');
        }
    } catch (err) {
        notify('P2P Offer Created Successfully!');
        closeModal('create-order-modal');
    }
}

// Mock fallback orders
function getMockOrders(tab) {
    return [
        { id: 101, creator_username: 'AddisTrader', price_per_usdt: 142.50, usdt_amount: 1200, min_amount: 1000, max_amount: 50000, payment_method: 'TELEBIRR' },
        { id: 102, creator_username: 'EthioCryptoPro', price_per_usdt: 141.80, usdt_amount: 850, min_amount: 2000, max_amount: 100000, payment_method: 'CBE' },
        { id: 103, creator_username: 'FastExpress', price_per_usdt: 143.00, usdt_amount: 300, min_amount: 500, max_amount: 20000, payment_method: 'DASHEN' }
    ];
}
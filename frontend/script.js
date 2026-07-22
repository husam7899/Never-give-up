const tg = window.Telegram.WebApp;
tg.ready();
tg.expand();

// Notification System
function notify(message, type = 'info') {
    const area = document.getElementById('notification-area');
    const el = document.createElement('div');
    el.className = `notify ${type}`;
    el.innerText = message;
    area.appendChild(el);
    setTimeout(() => el.remove(), 3000);
}

// Tab Switching
function switchTab(el, type) {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    el.classList.add('active');
    loadOrders(type);
}

// Load Orders
async function loadOrders(type) {
    const content = document.getElementById('content');
    try {
        const response = await fetch(`/api/orders?order_type=${type}`);
        const data = await response.json();
        
        if (!data || data.length === 0) {
            content.innerHTML = '<div style="text-align:center; padding:20px;">No orders found</div>';
            return;
        }

        content.innerHTML = data.map(o => `
            <div class="order-item">
                <div class="order-info">
                    <h4>${o.creator_username || 'Trader'}</h4>
                    <p>Price: <b>${o.price_per_usdt} ETB</b> | Limit: ${o.min_amount}-${o.max_amount}</p>
                </div>
                <button class="btn-trade" onclick="acceptOrder(${o.id})">Buy</button>
            </div>
        `).join('');
    } catch (e) {
        notify('Failed to load orders', 'error');
    }
}

// Trade Action
async function acceptOrder(id) {
    tg.HapticFeedback.impactOccurred('medium');
    const confirmed = confirm("Accept this trade order?");
    if (!confirmed) return;

    try {
        const res = await fetch('/api/orders/accept', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({order_id: id})
        });
        if (res.ok) {
            notify('Trade initiated successfully!');
            loadOrders('buy');
        } else {
            notify('Failed to accept trade', 'error');
        }
    } catch (e) {
        notify('Connection error', 'error');
    }
}

// Initial load
loadOrders('buy');
const tg = window.Telegram.WebApp;
tg.ready();

async function showSection(section) {
    const content = document.getElementById('content');
    content.innerHTML = `Loading ${section}...`;
    
    // Fetch data from backend
    const response = await fetch(`/api/orders?order_type=${section}`);
    const data = await response.json();
    
    content.innerHTML = data.map(order => `
        <div class="order-card">
            <h3>${order.creator_username}</h3>
            <p>Price: ${order.price_per_usdt} ETB</p>
            <button onclick="acceptOrder(${order.id})">Accept</button>
        </div>
    `).join('');
}

async function acceptOrder(id) {
    const response = await fetch('/api/orders/accept', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({order_id: id})
    });
    if(response.ok) alert('Order accepted!');
}

showSection('buy');
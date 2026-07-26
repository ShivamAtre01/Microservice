// ---- Health check bar ----
async function checkHealth() {
  const bar = document.getElementById("health-bar");
  bar.innerHTML = "";

  const services = [
    { name: "user-service", url: CONFIG.USER_SERVICE_URL },
    { name: "order-service", url: CONFIG.ORDER_SERVICE_URL },
    { name: "payment-service", url: CONFIG.PAYMENT_SERVICE_URL },
    { name: "notification-service", url: CONFIG.NOTIFICATION_SERVICE_URL },
  ];

  for (const svc of services) {
    const pill = document.createElement("span");
    pill.className = "health-pill";
    pill.textContent = `${svc.name}: checking...`;
    bar.appendChild(pill);

    try {
      const res = await fetch(`${svc.url}/health`);
      if (res.ok) {
        pill.textContent = `${svc.name}: UP`;
        pill.classList.add("up");
      } else {
        throw new Error("not ok");
      }
    } catch (e) {
      pill.textContent = `${svc.name}: DOWN`;
      pill.classList.add("down");
    }
  }
}

// ---- Users ----
async function loadUsers() {
  const tbody = document.querySelector("#users-table tbody");
  tbody.innerHTML = "<tr><td colspan='3'>Loading...</td></tr>";
  try {
    const res = await fetch(`${CONFIG.USER_SERVICE_URL}/users`);
    const users = await res.json();
    tbody.innerHTML = "";
    users.forEach((u) => {
      const tr = document.createElement("tr");
      tr.innerHTML = `<td>${u.id}</td><td>${u.name}</td><td>${u.email}</td>`;
      tbody.appendChild(tr);
    });
  } catch (e) {
    tbody.innerHTML = `<tr><td colspan='3'>Error: ${e.message}</td></tr>`;
  }
}

// ---- Orders ----
async function loadOrders() {
  const tbody = document.querySelector("#orders-table tbody");
  tbody.innerHTML = "<tr><td colspan='5'>Loading...</td></tr>";
  try {
    const res = await fetch(`${CONFIG.ORDER_SERVICE_URL}/orders`);
    const orders = await res.json();
    tbody.innerHTML = "";
    orders.forEach((o) => {
      const tr = document.createElement("tr");
      const paymentStatus = o.payment ? o.payment.status : "-";
      tr.innerHTML = `<td>${o.id}</td><td>${o.user_id}</td><td>₹${o.amount}</td><td>${o.status}</td><td>${paymentStatus}</td>`;
      tbody.appendChild(tr);
    });
  } catch (e) {
    tbody.innerHTML = `<tr><td colspan='5'>Error: ${e.message}</td></tr>`;
  }
}

async function placeOrder(event) {
  event.preventDefault();
  const resultEl = document.getElementById("order-result");
  resultEl.textContent = "Placing order...";

  const userId = document.getElementById("order-user-id").value.trim();
  const items = document.getElementById("order-items").value
    .split(",")
    .map((s) => s.trim())
    .filter(Boolean);
  const amount = Number(document.getElementById("order-amount").value);

  try {
    const res = await fetch(`${CONFIG.ORDER_SERVICE_URL}/orders`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_id: userId, items, amount }),
    });
    const data = await res.json();
    resultEl.textContent = `HTTP ${res.status}\n` + JSON.stringify(data, null, 2);

    // Refresh dependent views
    loadOrders();
    loadNotifications();
  } catch (e) {
    resultEl.textContent = `Error: ${e.message}`;
  }
}

// ---- Notifications ----
async function loadNotifications() {
  const tbody = document.querySelector("#notifications-table tbody");
  tbody.innerHTML = "<tr><td colspan='4'>Loading...</td></tr>";
  try {
    const res = await fetch(`${CONFIG.NOTIFICATION_SERVICE_URL}/notifications`);
    const notifications = await res.json();
    tbody.innerHTML = "";
    notifications.forEach((n) => {
      const tr = document.createElement("tr");
      tr.innerHTML = `<td>${n.to}</td><td>${n.message}</td><td>${n.channel}</td><td>${new Date(n.timestamp).toLocaleString()}</td>`;
      tbody.appendChild(tr);
    });
  } catch (e) {
    tbody.innerHTML = `<tr><td colspan='4'>Error: ${e.message}</td></tr>`;
  }
}

// ---- Wire up events ----
document.getElementById("refresh-users").addEventListener("click", loadUsers);
document.getElementById("refresh-orders").addEventListener("click", loadOrders);
document.getElementById("refresh-notifications").addEventListener("click", loadNotifications);
document.getElementById("order-form").addEventListener("submit", placeOrder);

// Initial load
checkHealth();
loadUsers();
loadOrders();
loadNotifications();

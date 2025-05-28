const API_BASE = "http://localhost:8000";

if (!localStorage.getItem("access_token") && !location.href.endsWith("login.html")) {
  location.href = "login.html";
}

function login() {
  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;

  fetch(`${API_BASE}/auth/token`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password })
  })
    .then(res => res.ok ? res.json() : Promise.reject("Invalid"))
    .then(data => {
      localStorage.setItem("access_token", data.access_token);
      localStorage.setItem("user", JSON.stringify(data.user));
      window.location.href = "index.html";
    })
    .catch(() => document.getElementById("error").classList.remove("hidden"));
}

function logout() {
  localStorage.clear();
  location.href = "login.html";
}

function getAuthHeaders() {
  return {
    Authorization: `Bearer ${localStorage.getItem("access_token")}`
  };
}

function showUserInfo() {
  const user = JSON.parse(localStorage.getItem("user") || "{}");
  const info = document.getElementById("user-info");
  if (user && info) {
    info.innerHTML = `
      <div class="text-right text-sm">
        <div><strong>${user.first_name} ${user.last_name}</strong></div>
        <div>${user.email}</div>
        <button onclick="logout()" class="text-red-500 underline text-xs mt-1">Logout</button>
      </div>
    `;
  }
}

async function toggleProductInventory(productId, btn) {
  const containerId = `product-inventory-${productId}`;
  let container = document.getElementById(containerId);

  if (!container) {
    container = document.createElement("div");
    container.id = containerId;
    container.className = "ml-4 mt-2 space-y-2";
    btn.parentElement.appendChild(container);
  }

  if (container.hasChildNodes()) {
    container.innerHTML = ""; // collapse
    return;
  }

  const res = await fetch(`${API_BASE}/inventory/by-product/${productId}`, {
    headers: getAuthHeaders()
  });
  const items = await res.json();
  container.innerHTML = ""; // clear previous content
  items.forEach(i => {
    const div = document.createElement("div");
    div.className = "bg-gray-50 p-2 rounded border";
    div.innerHTML = `
      <div><strong>Location:</strong> ${i.location_name}</div>
      <div><strong>Qty:</strong> ${i.quantity} | <strong>Reorder @</strong> ${i.reorder_point}</div>
      <div>${i.in_stock ? "✅ In Stock" : "❌ Out of Stock"} ${i.needs_reorder ? "⚠️ Needs Reorder" : ""}</div>
    `;
    container.appendChild(div);
  });
}

async function toggleLocationInventory(locationId, btn) {
  const containerId = `location-inventory-${locationId}`;
  let container = document.getElementById(containerId);

  if (!container) {
    container = document.createElement("div");
    container.id = containerId;
    container.className = "ml-4 mt-2 space-y-2";
    btn.parentElement.appendChild(container);
  }

  if (container.hasChildNodes()) {
    container.innerHTML = "";
    return;
  }

  const res = await fetch(`${API_BASE}/inventory/by-location/${locationId}`, {
    headers: getAuthHeaders()
  });
  const items = await res.json();
  container.innerHTML = "";
  items.forEach(i => {
    const div = document.createElement("div");
    div.className = "bg-gray-50 p-2 rounded border";
    div.innerHTML = `
      <div><strong>Product:</strong> ${i.product_name}</div>
      <div><strong>Qty:</strong> ${i.quantity} | <strong>Reorder @</strong> ${i.reorder_point}</div>
      <div>${i.in_stock ? "✅ In Stock" : "❌ Out of Stock"} ${i.needs_reorder ? "⚠️ Needs Reorder" : ""}</div>
    `;
    container.appendChild(div);
  });
}

document.addEventListener("DOMContentLoaded", () => {
  showUserInfo();

  const productContainer = document.getElementById("products");
  const locationContainer = document.getElementById("locations");

  if (productContainer) {
    fetch(`${API_BASE}/products`, { headers: getAuthHeaders() })
      .then(res => res.json())
      .then(products => {
        productContainer.innerHTML = ""; // Clear existing
        products.forEach(p => {
          const div = document.createElement("div");
          div.className = "bg-white p-4 rounded shadow";
          div.innerHTML = `
            <h2 class="text-lg font-semibold">${p.name} (${p.sku})</h2>
            <p>${p.description}</p>
            <p class="mb-2 text-sm text-gray-600">Price: $${p.price.toFixed(2)}</p>
            <button onclick="toggleProductInventory(${p.id}, this)"
                    class="text-blue-600 underline text-sm">View Inventory</button>
          `;
          productContainer.appendChild(div);
        });
      });
  }

  if (locationContainer) {
    fetch(`${API_BASE}/locations`, { headers: getAuthHeaders() })
      .then(res => res.json())
      .then(locations => {
        locationContainer.innerHTML = ""; // Clear existing
        locations.forEach(l => {
          const div = document.createElement("div");
          div.className = "bg-white p-4 rounded shadow";
          div.innerHTML = `
            <h2 class="text-lg font-semibold">${l.name}</h2>
            <p>${l.address}</p>
            <p class="mb-2 text-sm text-gray-600">Capacity: ${l.capacity}</p>
            <button onclick="toggleLocationInventory(${l.id}, this)"
                    class="text-blue-600 underline text-sm">View Inventory</button>
          `;
          locationContainer.appendChild(div);
        });
      });
  }
});

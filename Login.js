// Base API configuration URL
const API_URL = "http://127.0.0.1:8000";
console.log("Login.js loaded successfully");

// Helper to get the auth header
function getAuthHeaders() {
    const token = localStorage.getItem("token");
    return {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
    };
}

// Global state to store items loaded from backend for frontend search filtering
let allItems = [];

// -- INITIALIZATION --
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('inventory-rows')) {
        renderDashboardUsername();
        fetchInventory();
        document.getElementById('productForm').addEventListener('submit', submitItemForm);
        document.getElementById('search').addEventListener('keyup', searchItem);
    }
});

function renderDashboardUsername() {
    const storedUsername = localStorage.getItem('username');
    const usernameElement = document.getElementById('dashboard-username');
    console.log(`[DASHBOARD] Loading username: ${storedUsername}`);
    if (usernameElement) {
        usernameElement.textContent = storedUsername || 'User';
    }
}

async function fetchInventory() {
    try {
        console.log("[INVENTORY] Fetching items from API...");
        const response = await fetch(`${API_URL}/items/`, {
            method: 'GET',
            headers: getAuthHeaders()
        });
        console.log(`[INVENTORY] Response status: ${response.status}`);
        if (response.ok) {
            allItems = await response.json();
            console.log(`[INVENTORY] Successfully fetched ${allItems.length} items`);
            renderTable(allItems);
        } else if (response.status === 401) {
            console.error("[INVENTORY] Authentication failed - redirecting to login");
            alert("Session expired. Please log in again");
            window.location.href = "Login.html";
        } else {
            console.error(`[INVENTORY] Failed to fetch inventory - Status: ${response.status}`);
        }
    } catch (error) {
        console.log("[INVENTORY] Error fetching inventory:", error);
    }
}

function renderTable(items) {
    const tbody = document.getElementById("inventory-rows");
    tbody.innerHTML = "";

    if (!items || items.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" style="text-align:center;">No items found.</td></tr>';
        return;
    }

    items.forEach(item => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td><strong>${item.name || 'Unnamed Item'}</strong></td>
            <td>${item.description || ''}</td>
            <td>${item.quantity ?? 0}</td>
            <td>$${item.price?.toFixed ? item.price.toFixed(2) : item.price || '0.00'}</td>
            <td>${item.created_at ? new Date(item.created_at).toLocaleString() : ''}</td>
            <td>
                <button class="btn btn-danger btn-sm" type="button" onclick="deleteItem(${item.id})">Delete</button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

function openModal() {
    const modal = document.getElementById('itemModal');
    if (!modal) return;
    document.getElementById('modal-title').innerText = 'Add New Item';
    document.getElementById('productForm').reset();
    modal.style.display = 'block';
}

function closeModal() {
    const modal = document.getElementById('itemModal');
    if (!modal) return;
    modal.style.display = 'none';
}

function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    window.location.href = 'Login.html';
}

window.onclick = function(event) {
    const modal = document.getElementById('itemModal');
    if (event.target === modal) {
        closeModal();
    }
};

async function submitItemForm(event) {
    event.preventDefault();
    const name = document.getElementById('item-name').value.trim();
    const description = document.getElementById('item-desc').value.trim();
    const quantity = Number(document.getElementById('item-qty').value);
    const price = Number(document.getElementById('item-price').value);

    console.log(`[SUBMIT] Creating item: ${name}, Qty: ${quantity}, Price: ${price}`);

    if (!name || Number.isNaN(quantity) || Number.isNaN(price)) {
        console.warn("[SUBMIT] Validation failed - missing required fields");
        alert('Please provide the item name, quantity, and price.');
        return;
    }

    try {
        console.log("[SUBMIT] Sending POST request to /items/");
        const response = await fetch(`${API_URL}/items/`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({
                name,
                description,
                quantity,
                price
            })
        });
        console.log(`[SUBMIT] Response status: ${response.status}`);
        
        if (response.ok) {
            const savedItem = await response.json();
            console.log(`[SUBMIT] Item saved successfully - ID: ${savedItem.id}`);
            await fetchInventory();
            closeModal();
        } else if (response.status === 401) {
            console.error("[SUBMIT] Authentication failed");
            alert('Session expired. Please log in again.');
            window.location.href = 'Login.html';
        } else {
            let errorText = response.statusText;
            try {
                const errorData = await response.json();
                errorText = formatBackendError(errorData.detail || errorData);
            } catch (e) {
                console.error('[SUBMIT] Error parsing backend error body:', e);
            }
            console.error(`[SUBMIT] Failed to save item: ${errorText}`);
            alert('Unable to save item: ' + errorText);
        }
    } catch (error) {
        console.error('[SUBMIT] Error saving item:', error);
    }
}

async function deleteItem(itemId) {
    if (!confirm('Delete this item?')) return;
    try {
        console.log(`[DELETE] Deleting item ID: ${itemId}`);
        const response = await fetch(`${API_URL}/items/${itemId}`, {
            method: 'DELETE',
            headers: getAuthHeaders()
        });
        console.log(`[DELETE] Response status: ${response.status}`);
        
        if (response.ok) {
            console.log(`[DELETE] Item ${itemId} deleted successfully`);
            await fetchInventory();
        } else if (response.status === 401) {
            console.error("[DELETE] Authentication failed");
            alert('Session expired. Please log in again.');
            window.location.href = 'Login.html';
        } else {
            console.error(`[DELETE] Failed to delete item - Status: ${response.status}`);
        }
    } catch (error) {
        console.error('[DELETE] Error deleting item:', error);
    }
}

function searchItem() {
    const query = document.getElementById('search').value.toLowerCase();
    const filtered = allItems.filter(item => {
        return item.name.toLowerCase().includes(query) ||
            (item.description || '').toLowerCase().includes(query);
    });
    renderTable(filtered);
}

// Register page logic
function registerPageInit() {
    const registerButton = document.querySelector('.btn-primary');
    if (!registerButton) return;
    registerButton.addEventListener('click', async (e) => {
        e.preventDefault();
        const fullname = document.getElementById('fullname').value.trim();
        const username = document.getElementById('username').value.trim();
        const email = document.getElementById('email').value.trim();
        const password = document.getElementById('password').value;
        const confirmPassword = document.getElementById('confirm_password').value;
        
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email)) {
            alert('Please enter a valid email address.');
            return;
        }
        if (!fullname || !username || !email || !password || !confirmPassword) {
            alert('Please complete all fields.');
            return;
        }
        if (password !== confirmPassword) {
            alert('Passwords do not match!');
            return;
        }
        if (password.length < 6) {
            alert('Password must be at least 6 characters long.');
            return;
        }
        try {
            const response = await fetch(`${API_URL}/users/register`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    fullname: fullname, 
                    username: username, 
                    email: email, 
                    password: password 
                })
            });
            if (response.ok) {
                alert('Account created successfully!');
                window.location.href = 'Login.html';
            } else {
                const errorData = await response.json();
                console.error('Registration failed:', errorData);
                alert('Error: ' + formatBackendError(errorData.detail || errorData));
            }
        }   catch (error) {
            console.error('Error connecting to the backend: ', error);
            alert('Unable to connect to the backend.');
            }
        console.log('Registering with:', {fullname, username, email, password});
        if (!fullname || !username || !email || !password || !confirmPassword) {
            alert('Please complete all fields.');
            return;
        }
        if (password !== confirmPassword) {
            alert('Passwords do not match!');
            return;
        }

        try {
            const response = await fetch(`${API_URL}/users/register`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ fullname, username, email, password })
            });
            if (response.ok) {
                alert('Account created successfully!');
                window.location.href = 'Login.html';
            } else {
                const errorData = await response.json();
                alert('Error: ' + formatBackendError(errorData.detail || errorData));
            }
        } catch (error) {
            console.error('Error connecting to the backend: ', error);
            alert('Unable to connect to the backend.');
        }
    });
}

function formatBackendError(errorData) {
    if (!errorData) return 'Unknown error';
    if (typeof errorData === 'string') return errorData;
    if (Array.isArray(errorData)) {
        return errorData.map(err => {
            if (typeof err === 'string') return err;
            if (err.msg) return err.msg;
            if (err.detail) return err.detail;
            return JSON.stringify(err);
        }).join('\n');
    }
    if (typeof errorData === 'object') {
        return Object.values(errorData).map(value => formatBackendError(value)).join('\n');
    }
    return String(errorData);
}

document.addEventListener('DOMContentLoaded', () => {
    if (document.body.classList.contains('auth-page')) {
        const pageTitle = document.querySelector('h2')?.innerText || '';
        if (pageTitle === 'Create Account') {
            registerPageInit();
        }
    }
});
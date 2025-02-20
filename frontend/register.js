const API_URL = 'http://localhost:8000';

async function register() {
    const userData = {
        first_name: document.getElementById('firstName').value,
        last_name: document.getElementById('lastName').value,
        department: document.getElementById('department').value,
        team: document.getElementById('team').value,
        position: document.getElementById('position').value,
        email: document.getElementById('email').value,
        password: document.getElementById('password').value
    };

    try {
        const response = await fetch(`${API_URL}/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(userData)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            window.location.href = 'thank-you.html';
        } else {
            showMessage(data.detail, 'error');
        }
    } catch (error) {
        showMessage('Ошибка при регистрации', 'error');
    }
}

function showMessage(text, type) {
    const messageElement = document.getElementById('message');
    messageElement.textContent = text;
    messageElement.className = `message ${type}`;
} 
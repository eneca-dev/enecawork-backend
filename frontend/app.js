const API_URL = 'http://localhost:8000';

function validateEmail(email) {
    // Регулярное выражение для проверки формата email
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

async function login() {
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    
    if (!validateEmail(email)) {
        showMessage('Пожалуйста, введите корректный email адрес', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Сохраняем данные
            localStorage.setItem('access_token', data.access_token);
            localStorage.setItem('refresh_token', data.refresh_token);
            localStorage.setItem('user_email', email);
            
            // Перенаправляем на dashboard
            window.location.href = 'dashboard.html';
        } else {
            showMessage(data.detail, 'error');
        }
    } catch (error) {
        showMessage('Ошибка при входе', 'error');
    }
}

async function signup() {
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    
    if (!validateEmail(email)) {
        showMessage('Пожалуйста, введите корректный email адрес', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/auth/signup`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showMessage('Регистрация успешна!', 'success');
        } else {
            showMessage(data.detail, 'error');
        }
    } catch (error) {
        showMessage('Ошибка при регистрации', 'error');
    }
}

async function loginWithGoogle() {
    try {
        const response = await fetch(`${API_URL}/auth/google/login`);
        const data = await response.json();
        window.location.href = data.url;
    } catch (error) {
        showMessage('Ошибка при входе через Google', 'error');
    }
}

function showMessage(text, type) {
    const messageElement = document.getElementById('message');
    messageElement.textContent = text;
    messageElement.className = `message ${type}`;
} 
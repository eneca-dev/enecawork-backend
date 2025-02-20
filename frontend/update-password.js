const API_URL = 'http://localhost:8000';

async function updatePassword() {
    const newPassword = document.getElementById('newPassword').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    
    if (newPassword !== confirmPassword) {
        showMessage('Пароли не совпадают', 'error');
        return;
    }

    // Получаем токен из URL
    const urlParams = new URLSearchParams(window.location.hash.replace('#', ''));
    console.log('Parsed params:', Object.fromEntries(urlParams));
    const token = urlParams.get('access_token');

    if (!token) {
        showMessage('Отсутствует токен для сброса пароля', 'error');
        return;
    }

    try {
        const response = await fetch(`${API_URL}/auth/update-password`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                access_token: token,
                new_password: newPassword
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showMessage('Пароль успешно обновлен', 'success');
            setTimeout(() => {
                window.location.href = 'index.html';
            }, 2000);
        } else {
            showMessage(data.detail, 'error');
        }
    } catch (error) {
        showMessage('Ошибка при обновлении пароля', 'error');
    }
}

function showMessage(text, type) {
    const messageElement = document.getElementById('message');
    messageElement.textContent = text;
    messageElement.className = `message ${type}`;
} 
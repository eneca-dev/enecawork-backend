const API_URL = 'http://localhost:8000';

async function resetPassword() {
    const email = document.getElementById('email').value;

    try {
        const response = await fetch(`${API_URL}/auth/reset-password`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showMessage('Инструкции по восстановлению пароля отправлены на вашу почту', 'success');
        } else {
            showMessage(data.detail, 'error');
        }
    } catch (error) {
        showMessage('Ошибка при отправке запроса', 'error');
    }
}

function showMessage(text, type) {
    const messageElement = document.getElementById('message');
    messageElement.textContent = text;
    messageElement.className = `message ${type}`;
} 
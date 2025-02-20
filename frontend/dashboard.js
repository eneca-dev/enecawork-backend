document.addEventListener('DOMContentLoaded', function() {
    // Проверяем авторизацию
    const token = localStorage.getItem('access_token');
    if (!token) {
        window.location.href = 'index.html';
        return;
    }

    // Получаем и отображаем email пользователя
    const userEmail = localStorage.getItem('user_email');
    document.getElementById('userEmail').textContent = userEmail || 'пользователь';
});

async function logout() {
    const API_URL = 'http://localhost:8000';
    
    try {
        const response = await fetch(`${API_URL}/auth/logout`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            }
        });

        if (response.ok) {
            // Очищаем локальное хранилище
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            localStorage.removeItem('user_email');
            
            // Перенаправляем на страницу входа
            window.location.href = 'index.html';
        }
    } catch (error) {
        console.error('Ошибка при выходе:', error);
    }
} 
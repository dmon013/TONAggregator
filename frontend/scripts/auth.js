// frontend/scripts/auth.js
// Базовый помощник аутентификации, в основном для доступа к данным пользователя Telegram на стороне клиента (небезопасная версия)
// Безопасные операции всегда полагаются на проверку initData на бэкенде.

function getTelegramUserUnsafe() {
    if (window.Telegram && window.Telegram.WebApp && window.Telegram.WebApp.initDataUnsafe) {
        return window.Telegram.WebApp.initDataUnsafe.user || null;
    }
    console.warn("Telegram.WebApp.initDataUnsafe не доступен.");
    return null;
}

function getTelegramUserIdUnsafe() {
    const user = getTelegramUserUnsafe();
    return user? user.id : null;
}

// Эта функция может быть расширена, если потребуется более сложное состояние аутентификации на стороне клиента.
// На данный момент большая часть логики аутентификации такова:
// 1. Frontend отправляет initData с каждым API-запросом.
// 2. Backend проверяет initData для аутентификации и авторизации.
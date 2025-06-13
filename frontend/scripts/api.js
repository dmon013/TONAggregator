// frontend/scripts/api.js
const API_BASE_URL = '/api';

async function request(endpoint, method = 'GET', data = null) {
    const tg = window.Telegram.WebApp;
    if (!tg ||!tg.initData) {
        console.error("Telegram WebApp initData недоступны.");
        if (tg && tg.showAlert) tg.showAlert("Ошибка аутентификации.");
        throw new Error("Telegram initData недоступны.");
    }

    const headers = {
        'Authorization': `TmaInitData ${tg.initData}`,
        'Content-Type': 'application/json'
    };
    
    const config = { method, headers };
    if (data) config.body = JSON.stringify(data);

    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, config);
        const responseData = await response.json();
        if (!response.ok) throw new Error(responseData.error || `HTTP ошибка: ${response.status}`);
        return responseData;
    } catch (error) {
        console.error(`Ошибка API для ${endpoint}:`, error);
        if (tg && tg.showAlert) tg.showAlert(`Сетевая ошибка: ${error.message}`);
        throw error;
    }
}

// --- Публичные API ---
const api = {
    // Пользователи
    getMe: () => request('/users/me'),
    getRecentApps: () => request('/users/me/recent'),

    // Приложения
    getApps: (params = {}) => {
        const query = new URLSearchParams(params).toString();
        return request(`/apps?${query}`);
    },
    getAppDetails: (appId) => request(`/apps/${appId}`),
    logAppOpen: (appId) => request(`/apps/${appId}/open`, 'POST'),
    voteForApp: (appId) => request(`/apps/${appId}/vote`, 'POST'),

    // Категории
    getCategories: () => request('/categories'),

    // Подборки
    getFeaturedCollections: () => request('/collections/featured'),
    getCollectionDetails: (collectionId) => request(`/collections/${collectionId}`),

    // Новости (если будут добавлены)
    getNews: () => request('/news'),

    // --- Административные API ---
    admin: {
        addApp: (appData) => request('/apps', 'POST', appData),
        updateApp: (appId, appData) => request(`/apps/${appId}`, 'PUT', appData),
        deleteApp: (appId) => request(`/apps/${appId}`, 'DELETE'),
        //...здесь можно добавить функции для управления категориями, новостями и подборками
    }
};

// ИЗМЕНЕНИЕ: Отладки в браузере (необязательный кусок кода)
const isTgEnv = window.Telegram && window.Telegram.WebApp && window.Telegram.WebApp.initData;

async function request(endpoint, method = 'GET', data = null) {
    const tg = window.Telegram.WebApp;

    // ИЗМЕНЕНИЕ: Если мы не в среде Telegram, сразу возвращаем ошибку,
    // чтобы не вызывать методы, которые не поддерживаются (например, showAlert).
    if (!isTgEnv) {
        const errorMsg = "Telegram WebApp initData недоступны. Запустите приложение через Telegram.";
        console.error(errorMsg);
        // Возвращаем отклоненный Promise, чтобы вызывающий код мог обработать ошибку.
        return Promise.reject(new Error(errorMsg));
    }

    const headers = {
        'Authorization': `TmaInitData ${tg.initData}`,
        'Content-Type': 'application/json'
    };
    
    const config = { method, headers };
    if (data) config.body = JSON.stringify(data);

    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, config);
        const responseData = await response.json();
        if (!response.ok) throw new Error(responseData.error || `HTTP ошибка: ${response.status}`);
        return responseData;
    } catch (error) {
        console.error(`Ошибка API для ${endpoint}:`, error);
        // ИЗМЕНЕНИЕ: Проверяем, существует ли метод, перед вызовом
        if (tg && tg.showAlert) {
            tg.showAlert(`Сетевая ошибка: ${error.message}`);
        }
        throw error;
    }
}
// frontend/scripts/favorites.js

// Этот файл будет содержать функции для взаимодействия с API избранного
// и потенциально управлять локальным кэшем идентификаторов избранного для более быстрого обновления UI.
// main.js будет вызывать эти функции.

async function toggleFavoriteStatus(appId, isCurrentlyFavorite) {
    const tg = window.Telegram.WebApp;
    try {
        if (isCurrentlyFavorite) {
            await removeAppFromFavorites(appId);
            if (tg && tg.HapticFeedback) tg.HapticFeedback.notificationOccurred('success');
            // tg.showAlert(`Приложение удалено из избранного.`); // Можно раскомментировать для отладки
            return false; // Теперь не в избранном
        } else {
            await addAppToFavorites(appId);
            if (tg && tg.HapticFeedback) tg.HapticFeedback.notificationOccurred('success');
            // tg.showAlert(`Приложение добавлено в избранное!`); // Можно раскомментировать для отладки
            return true; // Теперь в избранном
        }
    } catch (error) {
        console.error("Не удалось переключить статус избранного:", error);
        // Сообщение об ошибке уже должно быть показано функцией request в api.js
        return isCurrentlyFavorite; // Вернуть исходный статус при ошибке
    }
}

// Функция для проверки, находится ли приложение в избранном (можно один раз загрузить все избранное и проверять локально)
// Обычно это управляется main.js путем загрузки всего избранного и передачи его или хранения глобально.
// Для простоты мы предполагаем, что элемент UI, вызывающий toggleFavoriteStatus, знает текущее состояние.
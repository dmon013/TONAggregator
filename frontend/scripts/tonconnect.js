// frontend/scripts/tonconnect.js
document.addEventListener('DOMContentLoaded', () => {
    const tg = window.Telegram.WebApp;
    const tonConnectButton = document.getElementById('ton-connect-btn');

    if (!window.TonConnectSDK) {
        console.error("TonConnectSDK не загружен!");
        if (tonConnectButton) tonConnectButton.textContent = "Ошибка TON SDK";
        return;
    }
    const TonConnectSDK = window.TonConnectSDK; // Используем глобальный SDK

    let connector;
    try {
        connector = new TonConnectSDK.TonConnect({
            // manifestUrl должен быть абсолютным URL к вашему tonconnect-manifest.json
            // window.location.origin может не работать корректно в некоторых средах TMA, лучше указать явно при сборке/развертывании
            manifestUrl: `${window.location.origin}/tonconnect-manifest.json` 
        });
    } catch (e) {
        console.error("Ошибка инициализации TonConnect:", e);
        if (tonConnectButton) tonConnectButton.textContent = "Ошибка TON Init";
        return;
    }


    async function updateButtonState(wallet) {
        if (!tonConnectButton) return;
        if (wallet && wallet.account && wallet.account.address) {
            const address = TonConnectSDK.toUserFriendlyAddress(wallet.account.address, wallet.account.chain === TonConnectSDK.CHAIN.TESTNET);
            tonConnectButton.textContent = `Кошелек: ${address.substring(0, 6)}...${address.substring(address.length - 4)}`;
            tonConnectButton.onclick = async () => {
                try {
                    await connector.disconnect();
                    if (tg.HapticFeedback) tg.HapticFeedback.notificationOccurred('warning');
                } catch (e) {
                    console.error("Ошибка отключения кошелька:", e);
                    if (tg.showAlert) tg.showAlert("Не удалось отключить кошелек.");
                }
            };
        } else {
            tonConnectButton.textContent = 'Подключить TON Кошелек';
            tonConnectButton.onclick = connectWallet; // Переназначаем обработчик
        }
    }

    async function connectWallet() {
        if (!connector) {
            if (tg.showAlert) tg.showAlert("TON Connect не инициализирован.");
            return;
        }
        try {
            const walletsList = await connector.getWallets();
            
            if (walletsList.length === 0) {
                if (tg.showAlert) tg.showAlert("Совместимые TON кошельки не найдены.");
                return;
            }

            // Показываем модальное окно Telegram для выбора кошелька (если их несколько)
            // или сразу инициируем подключение, если кошелек один или это предпочтительный метод.
            // Для простоты, используем универсальную ссылку первого доступного кошелька,
            // но в реальном приложении лучше дать пользователю выбор.
            
            // Пример простого выбора (можно улучшить, показав список в tg.showPopup)
            const connectionSource = {
                universalLink: walletsList.universalLink, // Используем первый кошелек для примера
                bridgeUrl: walletsList.bridgeUrl 
            };
            
            const universalLink = connector.connect(connectionSource);

            // Для мобильных кошельков, которые открываются по ссылке:
            // tg.openLink(universalLink); // Это может быть предпочтительнее для некоторых кошельков
            
            // Или показываем QR (если это десктоп и кошелек на телефоне) - требует генерации QR
            // В данном примере просто выводим информацию
            console.log("Ссылка для подключения (или для QR-кода):", universalLink);
            if (tg.showPopup) {
                 tg.showPopup({
                    title: "Подключение Кошелька",
                    message: "Следуйте инструкциям в вашем TON кошельке. Если вы на мобильном устройстве, кошелек должен открыться автоматически. На десктопе может потребоваться сканировать QR-код (не реализовано в демо).",
                    buttons: [{ type: 'ok'}]
                });
            }

        } catch (e) {
            console.error("Ошибка при попытке подключения к TON кошельку:", e);
            if (tg.showAlert) tg.showAlert(`Ошибка подключения кошелька: ${e.message || 'Неизвестная ошибка'}`);
        }
    }

    // Подписаться на изменения статуса подключения
    const unsubscribe = connector.onStatusChange(wallet => {
        updateButtonState(wallet);
        if (wallet && wallet.account) {
            console.log('TON Кошелек подключен:', wallet);
            // Здесь можно, например, отправить адрес кошелька на бэкенд для связки с профилем
            // или выполнить другие действия, требующие подключенного кошелька.
        } else {
            console.log('TON Кошелек отключен или статус изменился на неопределенный.');
        }
    }, (error) => { // Обработчик ошибок для onStatusChange
        console.error('Ошибка в onStatusChange TON Connect:', error);
        if (tg.showAlert) tg.showAlert(`Ошибка статуса TON Connect: ${error.message || 'Неизвестная ошибка'}`);
    });


    // Попытка восстановить существующее подключение при загрузке страницы
    connector.restoreConnection()
       .then(() => {
            updateButtonState(connector.wallet); // Обновляем состояние кнопки после восстановления
        })
       .catch(error => {
            console.warn("Не удалось восстановить сессию TON Connect:", error);
            // Это ожидаемо, если пользователь не подключался ранее или сессия истекла
            updateButtonState(null); // Убедимся, что кнопка в состоянии "Подключить"
        });
    
    // Устанавливаем начальное состояние кнопки (на случай если restoreConnection еще не завершился)
    updateButtonState(connector.wallet);

    // Очистка подписки при закрытии/уничтожении приложения (если это возможно в контексте TMA)
    // window.addEventListener('beforeunload', () => {
    //     unsubscribe();
    // });
});
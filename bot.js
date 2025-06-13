// bot.js
const TelegramBot = require('node-telegram-bot-api');
require('dotenv').config(); // Для загрузки BOT_TOKEN из файла.env

const token = process.env.TELEGRAM_BOT_TOKEN;
const webAppUrl = process.env.TELEGRAM_WEB_APP_URL; // например, ваш URL Firebase хостинга

if (!token ||!webAppUrl) {
    console.error("Ошибка: TELEGRAM_BOT_TOKEN или TELEGRAM_WEB_APP_URL не определены в.env или переменных окружения.");
    process.exit(1);
}

const bot = new TelegramBot(token, { polling: true });

bot.onText(/\/start/, (msg) => {
    const chatId = msg.chat.id;
    bot.sendMessage(chatId, "Добро пожаловать в наш Магазин Приложений! Нажмите ниже, чтобы открыть.", {
        reply_markup: {
            inline_keyboard: [{ text: 'Открыть Магазин', web_app: { url: webAppUrl } }]
        }
    });
});

bot.onText(/\/store/, (msg) => {
    const chatId = msg.chat.id;
    bot.sendMessage(chatId, "Открыть наш Магазин Приложений:", {
        reply_markup: {
            keyboard: [{ text: '🛍️ Открыть Магазин', web_app: { url: webAppUrl } }],
            resize_keyboard: true,
            one_time_keyboard: false // Оставить клавиатуру открытой
        }
    });
});

// Обработка данных, отправленных из Web App
bot.on('message', async (msg) => {
    if (msg.web_app_data) {
        console.log('Получены данные из Web App:', msg.web_app_data.data);
        try {
            const data = JSON.parse(msg.web_app_data.data);
            // Обработайте данные здесь, например, если TMA отправляет запрос на уведомление
            bot.sendMessage(msg.chat.id, `Получено из TMA: ${data.message}`);
        } catch (e) {
            console.error('Ошибка парсинга данных Web App:', e);
            bot.sendMessage(msg.chat.id, "Получены данные из TMA, но не удалось их разобрать.");
        }
    }
});

console.log(`Бот запущен... URL TMA: ${webAppUrl}`);
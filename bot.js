// bot.js

// Подключаем библиотеку
const TelegramBot = require('node-telegram-bot-api');

// Вставьте сюда токен вашего бота из BotFather
const TOKEN = '7684115873:AAGyGp2gODWZLp07fSWksdosDERCXNPS084';

// URL вашего Web App (например, Firebase Hosting): 
// должно быть что-то вроде: https://my-project.web.app
const WEBAPP_URL = 'https://tonaggregator.web.app';

// Запускаем бота в режиме polling
const bot = new TelegramBot(TOKEN, { polling: true });

// Обработчик команды /start
bot.onText(/\/start/, async (msg) => {
  const chatId = msg.chat.id;

  // Создаём объект кнопки Web App
  const webAppButton = {
    text: '🚀 Открыть TONAggregator',
    web_app: { url: WEBAPP_URL }
  };

  // Упаковываем кнопку в inline-клавиатуру
  const inlineKeyboard = {
    reply_markup: {
      inline_keyboard: [
        [ webAppButton ]  // одна строка, одна кнопка
      ]
    }
  };

  // Отправляем сообщение с Web App-кнопкой
  await bot.sendMessage(
    chatId,
    'Добро пожаловать! Нажмите кнопку ниже, чтобы открыть Web App:',
    inlineKeyboard
  );
});

console.log('Бот запущен и слушает /start...');

// frontend/scripts/main.js
document.addEventListener('DOMContentLoaded', () => {
    const tg = window.Telegram.WebApp;
    tg.ready();
    tg.expand();
    
    // --- Настройка темы ---
    const root = document.documentElement;
    root.style.setProperty('--telegram-bg-color', tg.themeParams.bg_color);
    root.style.setProperty('--telegram-text-color', tg.themeParams.text_color);
    root.style.setProperty('--telegram-hint-color', tg.themeParams.hint_color);
    root.style.setProperty('--telegram-link-color', tg.themeParams.link_color);
    root.style.setProperty('--telegram-button-color', tg.themeParams.button_color);
    root.style.setProperty('--telegram-button-text-color', tg.themeParams.button_text_color);
    root.style.setProperty('--telegram-secondary-bg-color', tg.themeParams.secondary_bg_color);

    // --- Глобальное состояние ---
    let currentUser = null;
    let viewHistory = ['main-view'];

    // --- Получение ссылок на DOM-элементы ---
    const views = document.querySelectorAll('.view');
    const navButtons = document.querySelectorAll('.nav-btn');
    const mainView = document.getElementById('main-view');
    const detailView = document.getElementById('detail-view');
    const listView = document.getElementById('list-view');
    const adminView = document.getElementById('admin-view');

    // --- Навигация ---
    function navigateTo(viewId, context = {}) {
        if (viewId!== viewHistory[viewHistory.length - 1]) {
            viewHistory.push(viewId);
        }
        
        views.forEach(view => view.classList.remove('active'));
        const targetView = document.getElementById(viewId);
        if (targetView) {
            targetView.classList.add('active');
            tg.BackButton.isVisible = viewHistory.length > 1;
        }

        // Загрузка контента для нового экрана
        switch (viewId) {
            case 'main-view':
                loadHomePage();
                break;
            case 'detail-view':
                loadAppDetails(context.appId);
                break;
            case 'list-view':
                loadListView(context);
                break;
            case 'admin-view':
                loadAdminView();
                break;
        }
    }

    function navigateBack() {
        if (viewHistory.length <= 1) return;
        viewHistory.pop();
        const previousViewId = viewHistory[viewHistory.length - 1];
        
        views.forEach(view => view.classList.remove('active'));
        document.getElementById(previousViewId).classList.add('active');
        tg.BackButton.isVisible = viewHistory.length > 1;
    }

    tg.BackButton.onClick(navigateBack);
    document.querySelectorAll('.back-button').forEach(btn => btn.addEventListener('click', navigateBack));

    navButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const viewId = btn.dataset.view;
            const context = { type: btn.dataset.type }; // Для кнопки "Категории"
            viewHistory = ['main-view']; // Сброс истории при переключении через нижнюю панель
            navigateTo(viewId, context);
        });
    });

    // --- Рендеринг (Отрисовка) ---
    function renderSkeleton(container, template, count) {
        container.innerHTML = '';
        for (let i = 0; i < count; i++) {
            container.innerHTML += template;
        }
    }

    const recentSkeleton = `<div class="app-card-horizontal"><div class="skeleton skeleton-icon"></div><div class="skeleton skeleton-text"></div></div>`;
    const collectionSkeleton = `<div class="content-section"><div class="skeleton skeleton-text" style="width: 50%; height: 1.3em; margin-left: 15px;"></div><div class="horizontal-scroll-list">${recentSkeleton.repeat(3)}</div></div>`;
    const listSkeleton = `<div class="app-card-vertical"><div class="skeleton skeleton-icon"></div><div style="flex-grow: 1;"><div class="skeleton skeleton-text" style="width: 70%;"></div><div class="skeleton skeleton-text" style="width: 90%; height: 0.8em;"></div></div></div>`;

    function renderRecentApps(apps) {
        const container = document.getElementById('recent-apps-list');
        const section = document.getElementById('recent-section');
        if (!apps || apps.length === 0) {
            section.style.display = 'none';
            return;
        }
        section.style.display = 'block';
        container.innerHTML = '';
        apps.forEach(app => {
            const card = document.createElement('div');
            card.className = 'app-card-horizontal';
            card.innerHTML = `<img src="${app.iconUrl}" class="app-icon"><span class="app-name">${app.name}</span>`;
            card.addEventListener('click', () => navigateTo('detail-view', { appId: app.id }));
            container.appendChild(card);
        });
    }

    function renderCollection(collection) {
        const container = document.getElementById('collections-container');
        const section = document.createElement('section');
        section.className = 'content-section';
        section.innerHTML = `<h2>${collection.title} <button class="see-all-btn" data-id="${collection.id}">Смотреть всё →</button></h2>`;
        
        const list = document.createElement('div');
        list.className = 'horizontal-scroll-list';
        collection.apps.slice(0, 10).forEach(app => { // Показываем до 10 приложений
            const card = document.createElement('div');
            card.className = 'app-card-horizontal';
            card.innerHTML = `<img src="${app.iconUrl}" class="app-icon"><span class="app-name">${app.name}</span>`;
            card.addEventListener('click', () => navigateTo('detail-view', { appId: app.id }));
            list.appendChild(card);
        });
        section.appendChild(list);
        container.appendChild(section);

        section.querySelector('.see-all-btn').addEventListener('click', (e) => {
            const collectionId = e.target.dataset.id;
            navigateTo('list-view', { type: 'collection', id: collectionId, title: collection.title });
        });
    }

    function renderAppDetails(appId) {
        const container = document.getElementById('app-detail-content');
        container.innerHTML = `<p>Загрузка...</p>`; // Заглушка
        api.getAppDetails(appId).then(app => {
            document.getElementById('detail-app-name-header').textContent = app.name;
            container.innerHTML = `
                <div class="detail-header">
                    <img src="${app.iconUrl}" class="app-icon">
                    <div class="detail-title-group">
                        <h3 class="app-name">${app.name}</h3>
                        <p class="app-developer">${app.developerName || 'Неизвестный разработчик'}</p>
                    </div>
                </div>
                <div class="detail-stats">
                    <span>${app.votesCount || 0} голосов</span> • <span>${app.usageCount || 0} запусков</span>
                </div>
                <div class="detail-actions">
                    <button class="action-btn open-btn" data-link="${app.openLink}">Открыть</button>
                    <button class="action-btn secondary-btn" id="vote-btn">👍 Проголосовать</button>
                    <button class="action-btn secondary-btn" id="share-btn">🔗 Поделиться</button>
                </div>
                <div class="screenshots-gallery">
                    ${(app.screenshots || []).map(url => `<img src="${url}">`).join('')}
                </div>
                <div class="detail-description">
                    <h4>Описание</h4>
                    <p>${app.description || 'Описание отсутствует.'}</p>
                </div>
            `;
            // Обработчики кнопок
            container.querySelector('.open-btn').addEventListener('click', e => {
                api.logAppOpen(app.id);
                tg.openTelegramLink(e.target.dataset.link);
            });
            container.querySelector('#vote-btn').addEventListener('click', () => {
                api.voteForApp(app.id).then(() => tg.showAlert('Спасибо за ваш голос!'));
            });
            container.querySelector('#share-btn').addEventListener('click', () => {
                const shareLink = `https://t.me/YOUR_BOT_USERNAME?start=app_${app.id}`; // Замените на имя вашего бота
                tg.openTelegramLink(`https://t.me/share/url?url=${encodeURIComponent(shareLink)}&text=${encodeURIComponent(`Посмотри это приложение: ${app.name}`)}`);
            });
        });
    }

    function renderListView(context) {
        const container = document.getElementById('list-view-content');
        const titleEl = document.getElementById('list-view-title');
        titleEl.textContent = context.title || 'Список';
        renderSkeleton(container, listSkeleton, 10);

        let promise;
        if (context.type === 'collection') {
            promise = api.getCollectionDetails(context.id).then(data => data.apps);
        } else if (context.type === 'categories') {
            titleEl.textContent = 'Категории';
            promise = api.getCategories();
        } else { // Поиск
            titleEl.textContent = `Результаты по: "${context.query}"`;
            promise = api.getApps({ q: context.query });
        }

        promise.then(items => {
            container.innerHTML = '';
            if (context.type === 'categories') {
                // Рендерим список категорий
                items.forEach(cat => {
                    const itemEl = document.createElement('div');
                    itemEl.className = 'category-list-item'; // Нужен свой стиль
                    itemEl.innerHTML = `<h4>${cat.name}</h4>`;
                    itemEl.addEventListener('click', () => navigateTo('list-view', { type: 'category-apps', id: cat.id, title: cat.name }));
                    container.appendChild(itemEl);
                });
            } else {
                // Рендерим список приложений
                items.forEach(app => {
                    const card = document.createElement('div');
                    card.className = 'app-card-vertical';
                    card.innerHTML = `
                        <img src="${app.iconUrl}" class="app-icon">
                        <div class="app-info">
                            <h4 class="app-name">${app.name}</h4>
                            <p class="app-description">${app.description.substring(0, 50)}...</p>
                        </div>
                        <button class="open-btn">Открыть</button>
                    `;
                    card.addEventListener('click', () => navigateTo('detail-view', { appId: app.id }));
                    container.appendChild(card);
                });
            }
        });
    }

    // --- Загрузка данных ---
    function loadHomePage() {
        const collectionsContainer = document.getElementById('collections-container');
        renderSkeleton(document.getElementById('recent-apps-list'), recentSkeleton, 5);
        renderSkeleton(collectionsContainer, collectionSkeleton, 2);

        api.getMe().then(user => {
            currentUser = user;
            if (user.role === 'admin') {
                const adminBtn = document.createElement('button');
                adminBtn.dataset.view = 'admin-view';
                adminBtn.className = 'nav-btn';
                adminBtn.innerHTML = '⚙️<br><span>Админ</span>';
                adminBtn.addEventListener('click', () => navigateTo('admin-view'));
                document.getElementById('bottom-navigation').appendChild(adminBtn);
            }
        });
        api.getRecentApps().then(renderRecentApps);
        api.getFeaturedCollections().then(collections => {
            collectionsContainer.innerHTML = '';
            collections.forEach(renderCollection);
        });
    }
    
    function loadAdminView() {
        // Логика для заполнения форм в админке, например, загрузка списка категорий
        const categorySelect = document.getElementById('admin-app-categories');
        api.getCategories().then(categories => {
            categorySelect.innerHTML = categories.map(c => `<option value="${c.id}">${c.name}</option>`).join('');
        });
    }

    //Функция для откладки в браузере (необязательный кусок кода)
    async function initializeApp() {
        try {
            // ИЗМЕНЕНИЕ: Оборачиваем загрузку в try...catch, чтобы приложение не "падало"
            const favApps = await api.getMyFavoriteApps();
            userFavoritesCache = favApps.map(app => app.id);
        } catch (e) {
            console.error("Не удалось загрузить избранное при инициализации:", e.message);
            // Если мы не в Telegram, это ожидаемая ошибка. Просто инициализируем пустым массивом.
            userFavoritesCache = [];
        }
    }
    // --- Инициализация ---
    navigateTo('main-view');
});
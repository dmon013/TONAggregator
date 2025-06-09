import { fetchApplications } from './api.js';
import { toggleFavorite, loadFavorites } from './favorites.js';
import { saveToLocalStorage, loadFromLocalStorage } from './utils.js';

let apps = [];
let userId = 'anonymous'; // позже можно будет получать настоящий userId если есть авторизация
let favorites = new Set();

async function init() {
  try {
    apps = await fetchApplications();
    favorites = await loadFavorites(userId);

    renderAppList();
    setupEventHandlers();
  } catch (err) {
    console.error('Ошибка инициализации:', err);
  }
}

function renderAppList() {
  const container = document.getElementById('allAppsList');
  if (!container) return;
  container.innerHTML = '';
  apps.forEach(app => {
    const item = document.createElement('div');
    item.className = 'card-app';
    item.innerHTML = `
      <div class="card-body">
        <img src="${app.icon || './icon/placeholder.png'}" alt="${app.title}">
        <div class="info">
          <h5>${app.title}</h5>
          <p>${app.description || ''}</p>
          <small>${app.rating || 0} ★</small>
        </div>
        <span class="favorite-star ${favorites.has(app.id) ? 'filled' : ''}" data-app-id="${app.id}">★</span>
      </div>
    `;
    item.querySelector('.favorite-star').addEventListener('click', async (e) => {
      e.stopPropagation();
      await toggleFavorite(app.id, userId, favorites, renderAppList);
    });
    container.appendChild(item);
  });
}

function setupEventHandlers() {
  // Здесь можно добавить обработчики для поиска, фильтров и прочего
}

document.addEventListener('DOMContentLoaded', init);
import { addFavorite, removeFavorite, fetchFavorites } from './api.js';

export async function toggleFavorite(appId, userId, favoritesSet, onChange) {
  if (favoritesSet.has(appId)) {
    try {
      await removeFavorite(userId, appId);
      favoritesSet.delete(appId);
      onChange && onChange();
    } catch (err) {
      console.error('Не удалось удалить из избранного:', err);
    }
  } else {
    try {
      await addFavorite(userId, appId);
      favoritesSet.add(appId);
      onChange && onChange();
    } catch (err) {
      console.error('Не удалось добавить в избранное:', err);
    }
  }
}

export async function loadFavorites(userId) {
  try {
    const favs = await fetchFavorites(userId);
    return new Set(favs);
  } catch (err) {
    console.error('Ошибка загрузки избранного:', err);
    return new Set();
  }
}
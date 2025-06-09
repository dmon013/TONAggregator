const API_BASE = 'http://127.0.0.1:5001';

export async function fetchApplications() {
  const response = await fetch(`${API_BASE}/applications`);
  if (!response.ok) throw new Error('Ошибка загрузки приложений');
  return response.json();
}

export async function addFavorite(userId, appId) {
  const response = await fetch(`${API_BASE}/favorites`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ userId, appId })
  });
  if (!response.ok) throw new Error('Ошибка добавления в избранное');
  return response.json();
}

export async function removeFavorite(userId, appId) {
  const favId = `${userId}_${appId}`;
  const response = await fetch(`${API_BASE}/favorites/${favId}`, { method: 'DELETE' });
  if (!response.ok) throw new Error('Ошибка удаления из избранного');
  return response.json();
}

export async function fetchFavorites(userId) {
  const response = await fetch(`${API_BASE}/favorites/${userId}`);
  if (!response.ok) throw new Error('Ошибка получения избранных');
  return response.json();
}
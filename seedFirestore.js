// seedFirestore.js

// 1. Подключаем Firebase Admin SDK (CommonJS синтаксис)
const admin = require('firebase-admin');
const path = require('path');
const fs = require('fs');

// 2. Определяем, где лежит файл ключа сервисного аккаунта.
//    Допустим, мы сохранили его рядом с seedFirestore.js и назвали serviceAccountKey.json
const serviceAccountPath = path.join(__dirname, 'serviceAccountKey.json');

// 3. Проверяем, что файл действительно существует
if (!fs.existsSync(serviceAccountPath)) {
  console.error(`Ошибка: файл serviceAccountKey.json не найден по пути:\n  ${serviceAccountPath}\n` +
    `Проверьте, что вы скачали ключ из Firebase Console и поместили его именно туда.`);
  process.exit(1);
}

// 4. Инициализируем приложение админа, используя ключ из serviceAccountKey.json
admin.initializeApp({
  credential: admin.credential.cert(require(serviceAccountPath))
});

// 5. Получаем ссылку на Firestore
const db = admin.firestore();

async function seed() {
  // --- 1. users/user_1 ---
  await db.collection('users').doc('user_1').set({
    displayName: 'Alice',
    email: 'alice@example.com',
    photoURL: 'https://example.com/avatar.png',
    createdAt: admin.firestore.FieldValue.serverTimestamp(),
    language: 'ru',
    theme: 'light'
  });

  // --- 2. categories/finance ---
  await db.collection('categories').doc('finance').set({
    name: 'Финансы',
    slug: 'finances',
    description: 'Все финтех- и DeFi-приложения',
    createdAt: admin.firestore.FieldValue.serverTimestamp(),
    updatedAt: admin.firestore.FieldValue.serverTimestamp()
  });

  // --- 3. tags/defi ---
  await db.collection('tags').doc('defi').set({
    name: 'DeFi',
    slug: 'defi',
    createdAt: admin.firestore.FieldValue.serverTimestamp()
  });

  // --- 4. apps/app_1 ---
  await db.collection('apps').doc('app_1').set({
    title: 'Ston.fi',
    category: 'Финансы',
    description: 'DEX для обмена токенов.',
    rating: 4.8,
    iconURL: 'https://example.com/icons/stonfi.png',
    tags: ['defi', 'dex'],
    averageRating: 4.8,
    reviewsCount: 1,
    createdAt: admin.firestore.FieldValue.serverTimestamp(),
    updatedAt: admin.firestore.FieldValue.serverTimestamp()
  });

  // --- 5. appVersions/version_1 ---
  await db.collection('appVersions').doc('version_1').set({
    appRef: db.doc('apps/app_1'),
    snapshot: {
      title: 'Ston.fi',
      category: 'Финансы',
      description: 'DEX для обмена токенов.',
      rating: 4.8,
      iconURL: 'https://example.com/icons/stonfi.png'
    },
    versionNumber: 1,
    changedBy: db.doc('users/user_1'),
    changedAt: admin.firestore.FieldValue.serverTimestamp(),
    changeType: 'create'
  });

  // --- 6. reviews/{autoID} ---
  const reviewRef = db.collection('reviews').doc();
  await reviewRef.set({
    userRef: db.doc('users/user_1'),
    appRef: db.doc('apps/app_1'),
    rating: 5,
    comment: 'Отличное приложение, рекомендую!',
    createdAt: admin.firestore.FieldValue.serverTimestamp(),
    updatedAt: admin.firestore.FieldValue.serverTimestamp()
  });

  // --- 7. comments/{autoID} ---
  const commentRef = db.collection('comments').doc();
  await commentRef.set({
    userRef: db.doc('users/user_1'),
    appRef: db.doc('apps/app_1'),
    text: 'Мне понравился функционал, спасибо!',
    parentRef: null,
    createdAt: admin.firestore.FieldValue.serverTimestamp(),
    updatedAt: admin.firestore.FieldValue.serverTimestamp()
  });

  // --- 8. favorites/user_1_app_1 ---
  await db.collection('favorites').doc('user_1_app_1').set({
    userRef: db.doc('users/user_1'),
    appRef: db.doc('apps/app_1'),
    addedAt: admin.firestore.FieldValue.serverTimestamp()
  });

  // --- 9. searchHistory/{autoID} ---
  const shRef = db.collection('searchHistory').doc();
  await shRef.set({
    userRef: db.doc('users/user_1'),
    query: 'Ston.fi',
    createdAt: admin.firestore.FieldValue.serverTimestamp()
  });

  // --- 10. collectionsMeta/top3 ---
  await db.collection('collectionsMeta').doc('top3').set({
    title: '🔥 Подборки (Top 3)',
    appRefs: [
      db.doc('apps/app_1'),
      db.doc('apps/app_2'), // если они есть
      db.doc('apps/app_3')
    ],
    updatedAt: admin.firestore.FieldValue.serverTimestamp()
  });

  // --- 11. settings/global ---
  await db.collection('settings').doc('global').set({
    sortDefault: 'rating_desc',
    filterCategories: ['Финансы', 'Игры'],
    showRatings: true,
    updatedAt: admin.firestore.FieldValue.serverTimestamp()
  });

  // --- 12. notificationSettings/user_1 ---
  await db.collection('notificationSettings').doc('user_1').set({
    newAppRelease: true,
    newAppVersion: true,
    newReview: false,
    commentReply: true,
    updatedAt: admin.firestore.FieldValue.serverTimestamp()
  });

  // --- 13. subscriptions/user_1_app_1 ---
  await db.collection('subscriptions').doc('user_1_app_1').set({
    userRef: db.doc('users/user_1'),
    type: 'app',
    ref: db.doc('apps/app_1'),
    createdAt: admin.firestore.FieldValue.serverTimestamp()
  });

  // --- 14. auditLogs/{autoID} ---
  const auditRef = db.collection('auditLogs').doc();
  await auditRef.set({
    userRef: db.doc('users/user_1'),
    action: 'update_app',
    target: db.doc('apps/app_1'),
    details: {
      fieldChanged: 'rating',
      oldValue: 4.7,
      newValue: 4.8
    },
    createdAt: admin.firestore.FieldValue.serverTimestamp()
  });

  // --- 15. userEvents/{autoID} ---
  const eventRef = db.collection('userEvents').doc();
  await eventRef.set({
    userRef: db.doc('users/user_1'),
    eventType: 'view_app',
    metadata: {
      appId: 'app_1',
      collectionKey: 'top3',
      searchQuery: 'Ston.fi'
    },
    timestamp: admin.firestore.FieldValue.serverTimestamp()
  });

  console.log('Инициализация коллекций завершена.');
}

seed()
  .catch(err => {
    console.error('Произошла ошибка при заполнении Firestore:', err);
  })
  .finally(() => process.exit());

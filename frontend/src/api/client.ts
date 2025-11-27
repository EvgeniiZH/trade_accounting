import axios from 'axios';

const apiClient = axios.create({
  baseURL: '/api', // Vite будет проксировать на http://127.0.0.1:8000/api
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Для отправки cookies (сессионная авторизация Django)
});

// Получаем CSRF-токен из cookies Django
function getCookie(name: string): string | null {
  if (typeof document === 'undefined') return null;
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) {
    return parts.pop()!.split(';').shift() || null;
  }
  return null;
}

// Добавляем CSRF-заголовок для "опасных" запросов (POST/PUT/PATCH/DELETE)
apiClient.interceptors.request.use((config) => {
  const method = (config.method || 'get').toLowerCase();
  const unsafeMethods = ['post', 'put', 'patch', 'delete'];

  if (unsafeMethods.includes(method)) {
    const csrfToken = getCookie('csrftoken');
    if (csrfToken) {
      config.headers = config.headers || {};
      (config.headers as any)['X-CSRFToken'] = csrfToken;
    }
  }

  return config;
});

// Интерцептор для обработки ошибок
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Если не авторизован - редирект на страницу логина Django
      window.location.href = '/login/';
    }
    return Promise.reject(error);
  }
);

export default apiClient;

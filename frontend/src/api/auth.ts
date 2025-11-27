import apiClient from './client';

export const authApi = {
  // Проверить текущего пользователя (через Django сессию)
  getCurrentUser: async () => {
    try {
      // Используем любой защищённый endpoint для проверки авторизации
      const response = await apiClient.get('/items/', { params: { page_size: 1 } });
      return { authenticated: true };
    } catch (error: any) {
      if (error.response?.status === 401) {
        return { authenticated: false };
      }
      throw error;
    }
  },

  // Выход (через Django logout)
  logout: async () => {
    // Django logout обычно делается через POST на /logout/
    // Но для API можно просто очистить cookies на клиенте
    window.location.href = '/logout/';
  },
};


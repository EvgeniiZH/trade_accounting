import apiClient from './client';
import type { User, PaginatedResponse } from '../types.ts';

export const usersApi = {
  // Получить список пользователей
  getList: async (params?: { page?: number; search?: string }) => {
    const response = await apiClient.get<PaginatedResponse<User>>('/users/', {
      params,
    });
    return response.data;
  },

  // Получить детали пользователя
  getDetail: async (id: number) => {
    const response = await apiClient.get<User>(`/users/${id}/`);
    return response.data;
  },

  // Создать пользователя
  create: async (data: { username: string; email: string; password: string; is_admin?: boolean }) => {
    const response = await apiClient.post<User>('/users/', data);
    return response.data;
  },

  // Обновить пользователя
  update: async (id: number, data: Partial<{ username: string; email: string; is_admin: boolean }>) => {
    const response = await apiClient.put<User>(`/users/${id}/`, data);
    return response.data;
  },

  // Удалить пользователя
  delete: async (id: number) => {
    await apiClient.delete(`/users/${id}/`);
  },
};


import apiClient from './client';
import type { Item, PaginatedResponse } from '../types.ts';

export const itemsApi = {
  // Получить список товаров с поиском
  getList: async (params?: { page?: number; search?: string; ordering?: string }) => {
    const response = await apiClient.get<PaginatedResponse<Item>>('/items/', {
      params,
    });
    return response.data;
  },

  // Получить все товары (для селекта)
  getAll: async () => {
    const response = await apiClient.get<PaginatedResponse<Item>>('/items/', {
      params: { page_size: 1000 }, // Большой лимит для получения всех
    });
    return response.data.results;
  },

  // Создать товар
  create: async (data: { name: string; price: string }) => {
    const response = await apiClient.post<Item>('/items/', data);
    return response.data;
  },

  // Обновить товар
  update: async (id: number, data: { name: string; price: string }) => {
    const response = await apiClient.put<Item>(`/items/${id}/`, data);
    return response.data;
  },

  // Удалить товар
  delete: async (id: number) => {
    await apiClient.delete(`/items/${id}/`);
  },

  // Загрузить товары из Excel
  upload: async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await apiClient.post('/upload-items/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
};



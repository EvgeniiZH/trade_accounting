import apiClient from './client';
import type { Calculation, PaginatedResponse, CalculationCreateRequest } from '../types.ts';

export const calculationsApi = {
  // Получить список расчётов
  getList: async (params?: { page?: number; search?: string; ordering?: string }) => {
    const response = await apiClient.get<PaginatedResponse<Calculation>>('/calculations/', {
      params,
    });
    return response.data;
  },

  // Получить детали расчёта
  getDetail: async (id: number) => {
    const response = await apiClient.get<Calculation>(`/calculations/${id}/`);
    return response.data;
  },

  // Создать расчёт
  create: async (data: CalculationCreateRequest) => {
    const response = await apiClient.post<Calculation>('/calculations/', data);
    return response.data;
  },

  // Обновить расчёт
  update: async (id: number, data: CalculationCreateRequest) => {
    const response = await apiClient.put<Calculation>(`/calculations/${id}/`, data);
    return response.data;
  },

  // Удалить расчёт
  delete: async (id: number) => {
    await apiClient.delete(`/calculations/${id}/`);
  },

  // Копировать расчёт
  copy: async (id: number) => {
    const response = await apiClient.post<Calculation>(`/calculations/${id}/copy/`);
    return response.data;
  },

  // Сохранить снимок расчёта
  saveSnapshot: async (id: number) => {
    const response = await apiClient.post(`/calculations/${id}/save_snapshot/`);
    return response.data;
  },

  // Экспорт выбранных расчётов в Excel (ZIP)
  exportSelected: async (ids: number[]) => {
    const response = await apiClient.post('/calculations/export/', { ids }, {
      responseType: 'blob',
      // Снимаем автоматическую отправку JSON, чтобы не путать Django
      headers: { 'Content-Type': 'application/json' },
    });
    return response.data as Blob;
  },
};

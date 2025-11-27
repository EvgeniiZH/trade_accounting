import apiClient from './client';
import type { CalculationSnapshot, PaginatedResponse } from '../types.ts';

export const snapshotsApi = {
  // Получить список снимков
  getList: async (params?: { page?: number; search?: string }) => {
    const response = await apiClient.get<PaginatedResponse<CalculationSnapshot>>('/snapshots/', {
      params,
    });
    return response.data;
  },

  // Получить детали снимка
  getDetail: async (id: number) => {
    const response = await apiClient.get<CalculationSnapshot>(`/snapshots/${id}/`);
    return response.data;
  },
};


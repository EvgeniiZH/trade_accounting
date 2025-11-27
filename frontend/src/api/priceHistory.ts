import apiClient from './client';
import type { PriceHistory, PaginatedResponse } from '../types.ts';

export const priceHistoryApi = {
  // Получить историю цен
  getList: async (params?: { page?: number; search?: string }) => {
    const response = await apiClient.get<PaginatedResponse<PriceHistory>>('/price-history/', {
      params,
    });
    return response.data;
  },
};


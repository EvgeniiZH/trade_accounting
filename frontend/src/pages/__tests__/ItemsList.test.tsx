import React from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { MemoryRouter } from 'react-router-dom';
import { render, screen, waitFor } from '@testing-library/react';
import ItemsList from '../ItemsList';

// Мокаем API товаров, чтобы не ходить в бэкенд
vi.mock('../../api/items', () => ({
  itemsApi: {
    getList: vi.fn(async () => ({
      count: 1,
      results: [{ id: 1, name: 'Тестовый товар', price: '10.00' }],
    })),
    create: vi.fn(),
    update: vi.fn(),
    delete: vi.fn(),
    upload: vi.fn(),
  },
}));

function renderWithProviders(ui: React.ReactElement) {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });

  return render(
    <MemoryRouter>
      <QueryClientProvider client={queryClient}>{ui}</QueryClientProvider>
    </MemoryRouter>,
  );
}

describe('ItemsList page', () => {
  it('рендерит заголовок и строку товара', async () => {
    renderWithProviders(<ItemsList />);

    // Заголовок страницы
    expect(await screen.findByText(/Список товаров/i)).toBeInTheDocument();

    // Должен появиться тестовый товар из мока
    await waitFor(() => {
      expect(screen.getByText('Тестовый товар')).toBeInTheDocument();
    });
  });
});




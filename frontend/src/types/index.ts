// API Response types
export interface User {
  id: number;
  username: string;
  email: string;
  is_admin: boolean;
}

export interface Item {
  id: number;
  name: string;
  price: string; // Django DecimalField приходит как строка
}

export interface CalculationItem {
  id: number;
  item: number;
  item_name: string;
  item_price: string;
  quantity: number;
  total_price: string;
}

export interface Calculation {
  id: number;
  title: string;
  markup: string;
  created_at: string;
  created_by: string;
  total_price: string;
  total_price_with_markup: string;
  items_count: number;
  items?: CalculationItem[];
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

// Request types для создания/обновления расчёта
export interface CalculationCreateRequest {
  title: string;
  markup: number;
  items: Array<{
    item_id: number;
    quantity: number;
  }>;
}


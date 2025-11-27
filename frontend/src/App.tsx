import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { CssBaseline, ThemeProvider, createTheme } from '@mui/material';
import Layout from './components/Layout';
import ItemsList from './pages/ItemsList';
import CalculationsList from './pages/CalculationsList';
import CalculationCreateEdit from './pages/CalculationCreateEdit';
import SnapshotsList from './pages/SnapshotsList';
import PriceHistory from './pages/PriceHistory';
import UsersManagement from './pages/UsersManagement';
import Login from './pages/Login';

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function PrivateRoute({ children }: { children: React.ReactNode }) {
  // Простая проверка авторизации через попытку запроса
  // В реальном приложении можно использовать контекст или состояние
  return <>{children}</>;
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Router>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route
              path="/"
              element={
                <PrivateRoute>
                  <Layout>
                    <ItemsList />
                  </Layout>
                </PrivateRoute>
              }
            />
            <Route
              path="/calculations"
              element={
                <PrivateRoute>
                  <Layout>
                    <CalculationsList />
                  </Layout>
                </PrivateRoute>
              }
            />
            <Route
              path="/calculations/create"
              element={
                <PrivateRoute>
                  <Layout>
                    <CalculationCreateEdit />
                  </Layout>
                </PrivateRoute>
              }
            />
            <Route
              path="/calculations/:id/edit"
              element={
                <PrivateRoute>
                  <Layout>
                    <CalculationCreateEdit />
                  </Layout>
                </PrivateRoute>
              }
            />
            <Route
              path="/snapshots"
              element={
                <PrivateRoute>
                  <Layout>
                    <SnapshotsList />
                  </Layout>
                </PrivateRoute>
              }
            />
            <Route
              path="/price-history"
              element={
                <PrivateRoute>
                  <Layout>
                    <PriceHistory />
                  </Layout>
                </PrivateRoute>
              }
            />
            <Route
              path="/users"
              element={
                <PrivateRoute>
                  <Layout>
                    <UsersManagement />
                  </Layout>
                </PrivateRoute>
              }
            />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </Router>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;

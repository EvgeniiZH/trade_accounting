import React, { useState, useRef, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Container,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  CircularProgress,
  Alert,
  TextField,
  Box,
  Pagination,
  Typography,
  IconButton,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  InputAdornment,
  TableSortLabel,
  Snackbar,
  Tooltip,
} from '@mui/material';
import {
  Edit as EditIcon,
  Delete as DeleteIcon,
  Add as AddIcon,
  Upload as UploadIcon,
  Download as DownloadIcon,
  Search as SearchIcon,
  Close as CloseIcon,
} from '@mui/icons-material';
import { itemsApi } from '../api/items';
import type { Item } from '../types.ts';
import { useDebounce } from '../hooks/useDebounce';

export default function ItemsList() {
  const queryClient = useQueryClient();
  const [page, setPage] = useState(1);
  const [searchInput, setSearchInput] = useState('');
  const [ordering, setOrdering] = useState<string>('name');
  const [openDialog, setOpenDialog] = useState(false);
  const [editingItem, setEditingItem] = useState<Item | null>(null);
  const [newItem, setNewItem] = useState({ name: '', price: '' });
  const [snackbar, setSnackbar] = useState<{ open: boolean; message: string; severity: 'success' | 'error' }>({
    open: false,
    message: '',
    severity: 'success',
  });
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const searchInputRef = useRef<HTMLInputElement>(null);
  const debouncedSearch = useDebounce(searchInput, 500);

  // При изменении поискового запроса просто переходим на первую страницу,
  // но не трогаем само поле ввода, чтобы не терять фокус
  useEffect(() => {
    setPage(1);
  }, [debouncedSearch]);

  const { data, isLoading, error } = useQuery({
    queryKey: ['items', page, debouncedSearch, ordering],
    queryFn: () => {
      console.log('🔍 API запрос:', { page, search: debouncedSearch, ordering });
      return itemsApi.getList({ 
        page, 
        search: debouncedSearch || undefined,
        ordering 
      });
    },
  });
  // Настоящая "первая загрузка" — только когда ещё нет данных и нет поискового запроса
  const isFirstLoad = isLoading && !data && !searchInput && page === 1 && ordering === 'name';

  const createMutation = useMutation({
    mutationFn: itemsApi.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['items'] });
      setOpenDialog(false);
      setNewItem({ name: '', price: '' });
      setSnackbar({ open: true, message: 'Товар успешно создан!', severity: 'success' });
    },
    onError: (error: any) => {
      setSnackbar({ open: true, message: error.response?.data?.error || 'Ошибка создания товара', severity: 'error' });
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: { name: string; price: string } }) =>
      itemsApi.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['items'] });
      setOpenDialog(false);
      setEditingItem(null);
      setSnackbar({ open: true, message: 'Товар успешно обновлён!', severity: 'success' });
    },
    onError: (error: any) => {
      setSnackbar({ open: true, message: error.response?.data?.error || 'Ошибка обновления товара', severity: 'error' });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: itemsApi.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['items'] });
      setSnackbar({ open: true, message: 'Товар успешно удалён!', severity: 'success' });
    },
    onError: (error: any) => {
      setSnackbar({ open: true, message: error.response?.data?.error || 'Ошибка удаления товара', severity: 'error' });
    },
  });

  const uploadMutation = useMutation({
    mutationFn: itemsApi.upload,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['items'] });
      setUploadFile(null);
      setSnackbar({
        open: true,
        message: `Загружено! Добавлено: ${data.created}, Обновлено: ${data.updated}, Пропущено: ${data.skipped}`,
        severity: 'success',
      });
    },
    onError: (error: any) => {
      setSnackbar({ open: true, message: error.response?.data?.error || 'Ошибка загрузки файла', severity: 'error' });
    },
  });

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value;
    console.log('📝 Ввод:', newValue);
    setSearchInput(newValue);
  };

  const handleClearSearch = () => {
    console.log('🗑️ Очистка поиска');
    setSearchInput('');
    setPage(1);
    if (searchInputRef.current) {
      searchInputRef.current.focus();
    }
  };

  const handleSort = (field: string) => {
    if (ordering === field) {
      setOrdering(`-${field}`);
    } else if (ordering === `-${field}`) {
      setOrdering('name');
    } else {
      setOrdering(field);
    }
    setPage(1);
  };

  const handleOpenDialog = (item?: Item) => {
    if (item) {
      setEditingItem(item);
      setNewItem({ name: item.name, price: item.price });
    } else {
      setEditingItem(null);
      setNewItem({ name: '', price: '' });
    }
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setEditingItem(null);
    setNewItem({ name: '', price: '' });
  };

  const handleSave = () => {
    if (!newItem.name || !newItem.price) {
      setSnackbar({ open: true, message: 'Заполните все поля', severity: 'error' });
      return;
    }
    if (editingItem) {
      updateMutation.mutate({ id: editingItem.id, data: newItem });
    } else {
      createMutation.mutate(newItem);
    }
  };

  const handleDelete = (id: number) => {
    if (window.confirm('Вы уверены, что хотите удалить этот товар?')) {
      deleteMutation.mutate(id);
    }
  };

  const handleUpload = () => {
    if (!uploadFile) return;
    uploadMutation.mutate(uploadFile);
  };

  const handleDownloadTemplate = () => {
    window.location.href = '/api/download-template/';
  };

  const totalPages = data ? Math.ceil(data.count / 50) : 0;

  if (isFirstLoad) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Container maxWidth={false} disableGutters sx={{ mt: 4, px: { xs: 2, md: 3 } }}>
        <Alert severity="error">Ошибка загрузки данных: {String(error)}</Alert>
      </Container>
    );
  }

  return (
    <Container
      maxWidth={false}
      disableGutters
      sx={{ mt: 3, mb: 4, px: { xs: 2, md: 3 } }}
    >
      <Box
        display="flex"
        justifyContent="space-between"
        alignItems={{ xs: 'flex-start', sm: 'center' }}
        flexDirection={{ xs: 'column', sm: 'row' }}
        gap={2}
        mb={3}
      >
        <Typography variant="h4" component="h1" sx={{ fontSize: { xs: '1.5rem', md: '2rem' } }}>
          📦 Список товаров
        </Typography>
        <Box display="flex" gap={1} flexWrap="wrap" justifyContent={{ xs: 'flex-start', sm: 'flex-end' }}>
          <Button
            variant="outlined"
            startIcon={<DownloadIcon />}
            onClick={handleDownloadTemplate}
            sx={{ mr: 1 }}
          >
            Шаблон
          </Button>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => handleOpenDialog()}
          >
            Добавить товар
          </Button>
        </Box>
      </Box>

      <Box sx={{ mb: 3, display: 'flex', gap: 2, flexWrap: 'wrap' }}>
        <TextField
          fullWidth
          label="Поиск по названию"
          variant="outlined"
          value={searchInput}
          onChange={handleSearchChange}
          placeholder="Введите название товара..."
          autoComplete="off"
          inputRef={searchInputRef}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon />
              </InputAdornment>
            ),
            endAdornment: searchInput ? (
              <InputAdornment position="end">
                <IconButton size="small" onClick={handleClearSearch} edge="end">
                  <CloseIcon fontSize="small" />
                </IconButton>
              </InputAdornment>
            ) : null,
          }}
          sx={{ flex: 1, minWidth: 200 }}
        />
        <Button
          variant="outlined"
          component="label"
          startIcon={<UploadIcon />}
          disabled={uploadMutation.isPending}
        >
          Загрузить Excel
          <input
            type="file"
            hidden
            accept=".xlsx,.xls"
            onChange={(e) => {
              const file = e.target.files?.[0];
              if (file) {
                setUploadFile(file);
                uploadMutation.mutate(file);
              }
            }}
          />
        </Button>
      </Box>

      <TableContainer component={Paper} elevation={3} sx={{ width: '100%', overflowX: 'auto' }}>
        <Table>
          <TableHead>
            <TableRow sx={{ backgroundColor: '#1976d2' }}>
              <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>
                <TableSortLabel
                  active={ordering === 'name' || ordering === '-name'}
                  direction={ordering === 'name' ? 'asc' : ordering === '-name' ? 'desc' : undefined}
                  onClick={() => handleSort('name')}
                  sx={{ color: 'white !important' }}
                >
                  Название
                </TableSortLabel>
              </TableCell>
              <TableCell sx={{ color: 'white', fontWeight: 'bold' }} align="right">
                <TableSortLabel
                  active={ordering === 'price' || ordering === '-price'}
                  direction={ordering === 'price' ? 'asc' : ordering === '-price' ? 'desc' : undefined}
                  onClick={() => handleSort('price')}
                  sx={{ color: 'white !important' }}
                >
                  Цена
                </TableSortLabel>
              </TableCell>
              <TableCell sx={{ color: 'white', fontWeight: 'bold' }} align="center">
                Действия
              </TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {data?.results.map((item: Item) => (
              <TableRow key={item.id} sx={{ '&:hover': { backgroundColor: '#f5f5f5' } }}>
                <TableCell>{item.name}</TableCell>
                <TableCell align="right">{parseFloat(item.price).toFixed(2)} ₽</TableCell>
                <TableCell align="center">
                  <Tooltip title="Редактировать товар">
                    <IconButton size="small" color="primary" onClick={() => handleOpenDialog(item)}>
                      <EditIcon />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Удалить товар">
                    <IconButton size="small" color="error" onClick={() => handleDelete(item.id)}>
                      <DeleteIcon />
                    </IconButton>
                  </Tooltip>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {totalPages > 1 && (
        <Box sx={{ mt: 3, display: 'flex', justifyContent: 'center' }}>
          <Pagination
            count={totalPages}
            page={page}
            onChange={(_, value) => setPage(value)}
            color="primary"
            size="large"
          />
        </Box>
      )}

      <Box sx={{ mt: 2, textAlign: 'center' }}>
        <Typography variant="body2" color="textSecondary">
          Всего товаров: {data?.count || 0}
        </Typography>
      </Box>

      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <DialogTitle>{editingItem ? 'Редактировать товар' : 'Добавить товар'}</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2 }}>
            <TextField
              fullWidth
              label="Название"
              value={newItem.name}
              onChange={(e) => setNewItem({ ...newItem, name: e.target.value })}
              margin="normal"
              required
            />
            <TextField
              fullWidth
              label="Цена"
              type="number"
              value={newItem.price}
              onChange={(e) => setNewItem({ ...newItem, price: e.target.value })}
              margin="normal"
              required
              inputProps={{ step: '0.01', min: '0.01' }}
              InputProps={{
                endAdornment: <InputAdornment position="end">₽</InputAdornment>,
              }}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Отмена</Button>
          <Button
            onClick={handleSave}
            variant="contained"
            disabled={createMutation.isPending || updateMutation.isPending}
          >
            {editingItem ? 'Сохранить' : 'Создать'}
          </Button>
        </DialogActions>
      </Dialog>

      <Snackbar
        open={snackbar.open}
        </DialogActions>
      </Dialog>

      <Snackbar
        open={snackbar.open}
        </DialogActions>
      </Dialog>

      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
        message={snackbar.message}
      />
    </Container>
  );
}

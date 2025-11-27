import React, { useState, useEffect, useRef } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate, useParams } from 'react-router-dom';
import {
  Container,
  Paper,
  TextField,
  Button,
  Typography,
  Box,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  CircularProgress,
  Alert,
  Chip,
  InputAdornment,
  Autocomplete,
  Snackbar,
  Card,
  CardContent,
  Divider,
} from '@mui/material';
import {
  Delete as DeleteIcon,
  Add as AddIcon,
  Save as SaveIcon,
  ArrowBack as ArrowBackIcon,
  Remove as RemoveIcon,
} from '@mui/icons-material';
import { calculationsApi } from '../api/calculations';
import { itemsApi } from '../api/items';
import type { Item, Calculation, CalculationItem } from '../types.ts';
import { useDebounce } from '../hooks/useDebounce';

export default function CalculationCreateEdit() {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();
  const queryClient = useQueryClient();
  const isEdit = !!id;

  const [title, setTitle] = useState('');
  const [markup, setMarkup] = useState('0');
  const [selectedItems, setSelectedItems] = useState<Array<{ item: Item; quantity: number }>>([]);
  const [searchItem, setSearchItem] = useState('');
  const [snackbar, setSnackbar] = useState<{ open: boolean; message: string; severity: 'success' | 'error' }>({
    open: false,
    message: '',
    severity: 'success',
  });
  const searchItemInputRef = useRef<HTMLInputElement | null>(null);
  const [titleError, setTitleError] = useState(false);
  const [itemsError, setItemsError] = useState(false);
  const [isDirty, setIsDirty] = useState(false);
  const debouncedSearchItem = useDebounce(searchItem, 300);

  const { data: calculation, isLoading: loadingCalc } = useQuery({
    queryKey: ['calculation', id],
    queryFn: () => calculationsApi.getDetail(Number(id!)),
    enabled: isEdit,
  });

  const { data: itemsData, isLoading: loadingItems } = useQuery({
    queryKey: ['items', 'for-calculation', debouncedSearchItem],
    queryFn: () =>
      itemsApi.getList({
        page: 1,
        search: debouncedSearchItem || undefined,
        ordering: 'name',
      }),
  });

  useEffect(() => {
    if (calculation) {
      setTitle(calculation.title);
      setMarkup(calculation.markup);
      if (calculation.items) {
        const items = calculation.items.map((ci: CalculationItem) => ({
          item: { id: ci.item, name: ci.item_name, price: ci.item_price } as Item,
          quantity: ci.quantity,
        }));
        setSelectedItems(items);
      }
    }
  }, [calculation]);

  useEffect(() => {
    const handler = (event: BeforeUnloadEvent) => {
      if (!isDirty) return;
      event.preventDefault();
      event.returnValue = '';
    };
    window.addEventListener('beforeunload', handler);
    return () => window.removeEventListener('beforeunload', handler);
  }, [isDirty]);

  const createMutation = useMutation({
    mutationFn: calculationsApi.create,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['calculations'] });
      setSnackbar({ open: true, message: 'Расчёт успешно создан!', severity: 'success' });
      setTimeout(() => navigate('/calculations'), 1500);
    },
    onError: (error: any) => {
      setSnackbar({ open: true, message: error.response?.data?.error || 'Ошибка создания расчёта', severity: 'error' });
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: any }) => calculationsApi.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['calculations'] });
      setSnackbar({ open: true, message: 'Расчёт успешно обновлён!', severity: 'success' });
      setTimeout(() => navigate('/calculations'), 1500);
    },
    onError: (error: any) => {
      setSnackbar({ open: true, message: error.response?.data?.error || 'Ошибка обновления расчёта', severity: 'error' });
    },
  });

  const handleAddItem = (item: Item) => {
    if (selectedItems.find((si) => si.item.id === item.id)) {
      setSnackbar({ open: true, message: 'Товар уже добавлен', severity: 'error' });
      return;
    }
    setSelectedItems([...selectedItems, { item, quantity: 1 }]);
    setIsDirty(true);
    setSearchItem('');
    if (searchItemInputRef.current) {
      searchItemInputRef.current.focus();
    }
  };

  const handleRemoveItem = (itemId: number) => {
    setSelectedItems(selectedItems.filter((si) => si.item.id !== itemId));
    setIsDirty(true);
  };

  const handleQuantityChange = (itemId: number, quantity: number) => {
    if (quantity < 1) return;
    setSelectedItems(
      selectedItems.map((si) => (si.item.id === itemId ? { ...si, quantity } : si))
    );
    setIsDirty(true);
  };

  const calculateTotals = () => {
    const total = selectedItems.reduce(
      (sum, si) => sum + parseFloat(si.item.price) * si.quantity,
      0
    );
    const markupValue = parseFloat(markup) || 0;
    const totalWithMarkup = total + (total * markupValue) / 100;
    return { total, totalWithMarkup };
  };

  const handleSave = () => {
    const hasTitleError = !title.trim();
    const hasItemsError = selectedItems.length === 0;

    setTitleError(hasTitleError);
    setItemsError(hasItemsError);

    if (hasTitleError) {
      setSnackbar({ open: true, message: 'Введите название расчёта', severity: 'error' });
      return;
    }
    if (hasItemsError) {
      setSnackbar({ open: true, message: 'Добавьте хотя бы один товар', severity: 'error' });
      return;
    }

    const data = {
      title: title.trim(),
      markup: parseFloat(markup) || 0,
      items: selectedItems.map((si) => ({
        item_id: si.item.id,
        quantity: si.quantity,
      })),
    };

    if (isEdit) {
      updateMutation.mutate({ id: Number(id!), data });
    } else {
      createMutation.mutate(data);
    }
  };

  const { total, totalWithMarkup } = calculateTotals();
  const filteredItems =
    itemsData?.results.filter(
      (item) => !selectedItems.find((si) => si.item.id === item.id)
    ) || [];

  if (loadingCalc) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Box
        display="flex"
        alignItems="center"
        mb={3}
        gap={1}
      >
        <IconButton
          onClick={() => {
            if (isDirty) {
              const confirmLeave = window.confirm('У вас есть несохранённые изменения. Выйти без сохранения?');
              if (!confirmLeave) return;
            }
            navigate('/calculations');
          }}
          sx={{ mr: 1 }}
        >
          <ArrowBackIcon />
        </IconButton>
        <Typography variant="h4" component="h1" sx={{ fontSize: { xs: '1.6rem', md: '2rem' } }}>
          {isEdit ? 'Редактировать расчёт' : 'Создать расчёт'}
        </Typography>
      </Box>

      <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
        <Box
          sx={{
            mb: 3,
            display: 'flex',
            flexDirection: { xs: 'column', md: 'row' },
            gap: 2,
          }}
        >
          <TextField
            fullWidth
            label="Название расчёта"
            value={title}
            onChange={(e) => {
              const value = e.target.value;
              setTitle(value);
              if (titleError && value.trim()) setTitleError(false);
              setIsDirty(true);
            }}
            required
            error={titleError}
            helperText={titleError ? 'Введите название расчёта' : ''}
          />
          <TextField
            label="Наценка (%)"
            type="number"
            value={markup}
            onChange={(e) => {
              const raw = e.target.value.replace(',', '.');
              setMarkup(raw);
              setIsDirty(true);
            }}
            InputProps={{
              endAdornment: <InputAdornment position="end">%</InputAdornment>,
            }}
            inputProps={{ step: '0.1', min: '0' }}
            sx={{ width: { xs: '100%', md: 200 } }}
          />
        </Box>

        <Divider sx={{ my: 3 }} />

        <Typography variant="h6" gutterBottom>
          Добавить товары
        </Typography>
        <Autocomplete
          options={filteredItems}
          getOptionLabel={(option) => `${option.name} - ${parseFloat(option.price).toFixed(2)} ₽`}
          value={null}
          onChange={(_, newValue) => {
            if (newValue) handleAddItem(newValue);
          }}
          inputValue={searchItem}
          onInputChange={(_, newInputValue) => setSearchItem(newInputValue)}
          loading={loadingItems}
          renderInput={(params) => (
            <TextField
              {...params}
              inputRef={searchItemInputRef}
              label="Поиск товара"
              placeholder="Начните вводить название..."
            />
          )}
          sx={{ mb: 3 }}
        />

        {selectedItems.length > 0 && (
          <>
            <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
              Выбранные товары
            </Typography>
            <TableContainer sx={{ width: '100%', overflowX: 'auto' }}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Товар</TableCell>
                    <TableCell align="right">Цена</TableCell>
                    <TableCell align="center">Количество</TableCell>
                    <TableCell align="right">Итого</TableCell>
                    <TableCell align="center">Действия</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {selectedItems.map((si) => (
                    <TableRow key={si.item.id}>
                      <TableCell>{si.item.name}</TableCell>
                      <TableCell align="right">{parseFloat(si.item.price).toFixed(2)} ₽</TableCell>
                      <TableCell align="center">
                        <Box display="flex" alignItems="center" justifyContent="center" gap={1}>
                          <IconButton
                            size="small"
                            onClick={() => handleQuantityChange(si.item.id, si.quantity - 1)}
                          >
                            <RemoveIcon fontSize="small" />
                          </IconButton>
                          <TextField
                            type="number"
                            value={si.quantity}
                            onChange={(e) => handleQuantityChange(si.item.id, parseInt(e.target.value) || 1)}
                            inputProps={{ min: 1, style: { textAlign: 'center' } }}
                            sx={{ width: 80 }}
                          />
                          <IconButton
                            size="small"
                            onClick={() => handleQuantityChange(si.item.id, si.quantity + 1)}
                          >
                            <AddIcon fontSize="small" />
                          </IconButton>
                        </Box>
                      </TableCell>
                      <TableCell align="right">
                        {(parseFloat(si.item.price) * si.quantity).toFixed(2)} ₽
                      </TableCell>
                      <TableCell align="center">
                        <IconButton
                          size="small"
                          color="error"
                          onClick={() => handleRemoveItem(si.item.id)}
                        >
                          <DeleteIcon />
                        </IconButton>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </>
        )}
        {itemsError && (
          <Typography variant="body2" color="error" sx={{ mt: 1 }}>
            Добавьте хотя бы один товар в расчёт.
          </Typography>
        )}
      </Paper>

      <Box
        sx={{
          position: { xs: 'static', md: 'sticky' },
          bottom: 0,
          zIndex: (theme) => theme.zIndex.appBar,
          mt: 2,
        }}
      >
        <Card elevation={3}>
          <CardContent>
            <Box
              display="flex"
              justifyContent="space-between"
              alignItems={{ xs: 'flex-start', sm: 'center' }}
              flexDirection={{ xs: 'column', sm: 'row' }}
              gap={1}
            >
              <Typography variant="h6">Итого без наценки:</Typography>
              <Typography variant="h6">{total.toFixed(2)} ₽</Typography>
            </Box>
            <Box
              display="flex"
              justifyContent="space-between"
              alignItems={{ xs: 'flex-start', sm: 'center' }}
              flexDirection={{ xs: 'column', sm: 'row' }}
              gap={1}
              sx={{ mt: 1 }}
            >
              <Typography variant="h6" color="primary">
                Итого с наценкой ({markup}%):
              </Typography>
              <Typography variant="h5" color="primary" fontWeight="bold">
                {totalWithMarkup.toFixed(2)} ₽
              </Typography>
            </Box>

            <Box
              sx={{
                mt: 2,
                display: 'flex',
                justifyContent: { xs: 'stretch', sm: 'flex-end' },
                flexDirection: { xs: 'column', sm: 'row' },
                gap: 2,
              }}
            >
              <Button
                variant="outlined"
                onClick={() => {
                  if (isDirty) {
                    const confirmLeave = window.confirm(
                      'У вас есть несохранённые изменения. Выйти без сохранения?',
                    );
                    if (!confirmLeave) return;
                  }
                  navigate('/calculations');
                }}
              >
                Отмена
              </Button>
              <Button
                variant="contained"
                startIcon={<SaveIcon />}
                onClick={handleSave}
                disabled={createMutation.isPending || updateMutation.isPending}
                size="large"
              >
                {isEdit ? 'Сохранить' : 'Создать расчёт'}
              </Button>
            </Box>
          </CardContent>
        </Card>
      </Box>

      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
        message={snackbar.message}
      />
    </Container>
  );
}


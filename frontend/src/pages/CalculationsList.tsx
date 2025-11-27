import { useState, useRef, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
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
  InputAdornment,
  Snackbar,
  Chip,
  Menu,
  MenuItem,
  Checkbox,
  TableSortLabel,
} from '@mui/material';
import {
  Edit as EditIcon,
  Delete as DeleteIcon,
  Add as AddIcon,
  Search as SearchIcon,
  MoreVert as MoreVertIcon,
  ContentCopy as CopyIcon,
  Save as SaveIcon,
  Download as DownloadIcon,
  Close as CloseIcon,
} from '@mui/icons-material';
import { calculationsApi } from '../api/calculations';
import type { Calculation } from '../types.ts';
import { useDebounce } from '../hooks/useDebounce';

export default function CalculationsList() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [page, setPage] = useState(1);
  const [searchInput, setSearchInput] = useState('');
  const [ordering, setOrdering] = useState<string>('-created_at');
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [selectedCalc, setSelectedCalc] = useState<number | null>(null);
  const [selectedIds, setSelectedIds] = useState<number[]>([]);
  const [snackbar, setSnackbar] = useState<{ open: boolean; message: string; severity: 'success' | 'error' }>({
    open: false,
    message: '',
    severity: 'success',
  });
  const searchInputRef = useRef<HTMLInputElement>(null);
  const debouncedSearch = useDebounce(searchInput, 350);

  // При изменении поискового запроса переходим на первую страницу,
  // но не трогаем само поле ввода
  useEffect(() => {
    setPage(1);
  }, [debouncedSearch]);

  const { data, isLoading, error } = useQuery({
    queryKey: ['calculations', page, debouncedSearch, ordering],
    queryFn: () =>
      calculationsApi.getList({
        page,
        search: debouncedSearch || undefined,
        ordering,
      }),
  });
  const isFirstLoad = isLoading && !data && !searchInput && page === 1;

  const deleteMutation = useMutation({
    mutationFn: calculationsApi.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['calculations'] });
      setSnackbar({ open: true, message: 'Расчёт успешно удалён!', severity: 'success' });
    },
    onError: (error: any) => {
      setSnackbar({ open: true, message: error.response?.data?.error || 'Ошибка удаления', severity: 'error' });
    },
  });

  const copyMutation = useMutation({
    mutationFn: calculationsApi.copy,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['calculations'] });
      setSnackbar({ open: true, message: 'Расчёт успешно скопирован!', severity: 'success' });
    },
    onError: (error: any) => {
      setSnackbar({ open: true, message: error.response?.data?.error || 'Ошибка копирования', severity: 'error' });
    },
  });

  const saveSnapshotMutation = useMutation({
    mutationFn: calculationsApi.saveSnapshot,
    onSuccess: () => {
      setSnackbar({ open: true, message: 'Снимок расчёта успешно сохранён!', severity: 'success' });
    },
    onError: (error: any) => {
      setSnackbar({ open: true, message: error.response?.data?.error || 'Ошибка сохранения снимка', severity: 'error' });
    },
  });

  const exportMutation = useMutation({
    mutationFn: (ids: number[]) => calculationsApi.exportSelected(ids),
    onSuccess: (blob: Blob) => {
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = 'calculations.zip';
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      setSnackbar({ open: true, message: 'Экспорт успешно выполнен!', severity: 'success' });
    },
    onError: (error: any) => {
      setSnackbar({ open: true, message: error.response?.data?.error || 'Ошибка экспорта', severity: 'error' });
    },
  });

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchInput(e.target.value);
  };

  const handleClearSearch = () => {
    setSearchInput('');
    setPage(1);
    searchInputRef.current?.focus();
  };

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>, calcId: number) => {
    setAnchorEl(event.currentTarget);
    setSelectedCalc(calcId);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    setSelectedCalc(null);
  };

  const handleEdit = (calcId: number) => {
    navigate(`/calculations/${calcId}/edit`);
    handleMenuClose();
  };

  const handleDelete = (calcId: number) => {
    if (window.confirm('Вы уверены, что хотите удалить этот расчёт?')) {
      deleteMutation.mutate(calcId);
    }
    handleMenuClose();
  };

  const handleCopy = (calcId: number) => {
    copyMutation.mutate(calcId);
    handleMenuClose();
  };

  const handleSaveSnapshot = (calcId: number) => {
    saveSnapshotMutation.mutate(calcId);
    handleMenuClose();
  };

  const handleSort = (field: string) => {
    setPage(1);
    setOrdering((prev) => {
      if (prev === field) return `-${field}`;
      if (prev === `-${field}`) return field;
      return field;
    });
  };

  const handleToggleSelect = (id: number) => {
    setSelectedIds((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id],
    );
  };

  const handleSelectAll = () => {
    if (!data) return;
    const currentPageIds = data.results.map((calc) => calc.id);
    const allSelected = currentPageIds.every((id) => selectedIds.includes(id));
    if (allSelected) {
      setSelectedIds((prev) => prev.filter((id) => !currentPageIds.includes(id)));
    } else {
      setSelectedIds((prev) => Array.from(new Set([...prev, ...currentPageIds])));
    }
  };

  const handleExportSelected = () => {
    if (selectedIds.length === 0) return;
    exportMutation.mutate(selectedIds);
  };

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

  const totalPages = data ? Math.ceil(data.count / 50) : 0;

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
          📊 Список расчётов
        </Typography>
        <Box display="flex" gap={2} flexWrap="wrap" justifyContent={{ xs: 'flex-start', sm: 'flex-end' }}>
          <Button
            variant="outlined"
            startIcon={<DownloadIcon />}
            disabled={selectedIds.length === 0 || exportMutation.isPending}
            onClick={handleExportSelected}
          >
            Экспорт в Excel
          </Button>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => navigate('/calculations/create')}
          >
            Создать расчёт
          </Button>
        </Box>
      </Box>

      <Box sx={{ mb: 3 }}>
        <TextField
          fullWidth
          label="Поиск по названию"
          variant="outlined"
          value={searchInput}
          onChange={handleSearchChange}
          placeholder="Введите название расчёта..."
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
        />
      </Box>

      <TableContainer component={Paper} elevation={3} sx={{ width: '100%', overflowX: 'auto' }}>
        <Table>
          <TableHead>
            <TableRow sx={{ backgroundColor: '#1976d2' }}>
              <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>#</TableCell>
              <TableCell sx={{ color: 'white', fontWeight: 'bold' }} align="center">
                <Checkbox
                  sx={{ color: 'white' }}
                  indeterminate={
                    !!data &&
                    data.results.some((c) => selectedIds.includes(c.id)) &&
                    !data.results.every((c) => selectedIds.includes(c.id))
                  }
                  checked={!!data && data.results.every((c) => selectedIds.includes(c.id)) && data.results.length > 0}
                  onChange={handleSelectAll}
                  color="default"
                />
              </TableCell>
              <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>
                <TableSortLabel
                  active={ordering === 'title' || ordering === '-title'}
                  direction={ordering === 'title' ? 'asc' : 'desc'}
                  onClick={() => handleSort('title')}
                  sx={{ color: 'white !important' }}
                >
                  Название
                </TableSortLabel>
              </TableCell>
              <TableCell sx={{ color: 'white', fontWeight: 'bold' }} align="center">Товаров</TableCell>
              <TableCell sx={{ color: 'white', fontWeight: 'bold' }} align="right">
                <TableSortLabel
                  active={ordering === 'total_price' || ordering === '-total_price'}
                  direction={ordering === 'total_price' ? 'asc' : 'desc'}
                  onClick={() => handleSort('total_price')}
                  sx={{ color: 'white !important' }}
                >
                  Стоимость
                </TableSortLabel>
              </TableCell>
              <TableCell sx={{ color: 'white', fontWeight: 'bold' }} align="right">
                <TableSortLabel
                  active={
                    ordering === 'total_price_with_markup' || ordering === '-total_price_with_markup'
                  }
                  direction={ordering === 'total_price_with_markup' ? 'asc' : 'desc'}
                  onClick={() => handleSort('total_price_with_markup')}
                  sx={{ color: 'white !important' }}
                >
                  С наценкой
                </TableSortLabel>
              </TableCell>
              <TableCell sx={{ color: 'white', fontWeight: 'bold' }} align="center">
                <TableSortLabel
                  active={ordering === 'created_at' || ordering === '-created_at'}
                  direction={ordering === 'created_at' ? 'asc' : 'desc'}
                  onClick={() => handleSort('created_at')}
                  sx={{ color: 'white !important' }}
                >
                  Дата
                </TableSortLabel>
              </TableCell>
              <TableCell sx={{ color: 'white', fontWeight: 'bold' }} align="center">Действия</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {data?.results.map((calc: Calculation, index: number) => (
              <TableRow
                key={calc.id}
                sx={{ '&:hover': { backgroundColor: '#f5f5f5' }, cursor: 'pointer' }}
                onClick={() => navigate(`/calculations/${calc.id}/edit`)}
              >
                <TableCell>{(page - 1) * 50 + index + 1}</TableCell>
                <TableCell align="center" onClick={(e) => e.stopPropagation()}>
                  <Checkbox
                    checked={selectedIds.includes(calc.id)}
                    onChange={() => handleToggleSelect(calc.id)}
                    color="primary"
                  />
                </TableCell>
                <TableCell>
                  <Typography variant="body1" fontWeight="medium">
                    {calc.title}
                  </Typography>
                  {calc.created_by && (
                    <Typography variant="caption" color="textSecondary">
                      Автор: {calc.created_by}
                    </Typography>
                  )}
                </TableCell>
                <TableCell align="center">
                  <Chip label={calc.items_count} size="small" color="primary" variant="outlined" />
                </TableCell>
                <TableCell align="right">{parseFloat(calc.total_price).toFixed(2)} ₽</TableCell>
                <TableCell align="right">
                  <Typography variant="body1" fontWeight="bold" color="primary">
                    {parseFloat(calc.total_price_with_markup).toFixed(2)} ₽
                  </Typography>
                </TableCell>
                <TableCell align="center">
                  {new Date(calc.created_at).toLocaleDateString('ru-RU')}
                </TableCell>
                <TableCell align="center" onClick={(e) => e.stopPropagation()}>
                  <IconButton
                    size="small"
                    onClick={(e) => handleMenuOpen(e, calc.id)}
                  >
                    <MoreVertIcon />
                  </IconButton>
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
          Всего расчётов: {data?.count || 0}
        </Typography>
      </Box>

      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
      >
        <MenuItem onClick={() => selectedCalc && handleEdit(selectedCalc)}>
          <EditIcon sx={{ mr: 1 }} fontSize="small" />
          Редактировать
        </MenuItem>
        <MenuItem onClick={() => selectedCalc && handleCopy(selectedCalc)}>
          <CopyIcon sx={{ mr: 1 }} fontSize="small" />
          Копировать
        </MenuItem>
        <MenuItem onClick={() => selectedCalc && handleSaveSnapshot(selectedCalc)}>
          <SaveIcon sx={{ mr: 1 }} fontSize="small" />
          Сохранить снимок
        </MenuItem>
        <MenuItem onClick={() => selectedCalc && handleDelete(selectedCalc)} sx={{ color: 'error.main' }}>
          <DeleteIcon sx={{ mr: 1 }} fontSize="small" />
          Удалить
        </MenuItem>
      </Menu>

      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
        message={snackbar.message}
      />
    </Container>
  );
}

import React, { useState, useEffect } from 'react';
import { 
    Container, Typography, Table, TableBody, TableCell, 
    TableContainer, TableHead, TableRow, Paper, 
    TablePagination, TextField, InputAdornment, Box,
    IconButton, Button
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import DeleteIcon from '@mui/icons-material/Delete';
import EditIcon from '@mui/icons-material/Edit';
import AddIcon from '@mui/icons-material/Add';
import { getCalculations, deleteCalculation } from '../api/calculations';
import type { Calculation } from '../types.ts';

const CalculationsPage: React.FC = () => {
    const [calculations, setCalculations] = useState<Calculation[]>([]);
    const [loading, setLoading] = useState(false);
    const [page, setPage] = useState(0);
    const [rowsPerPage, setRowsPerPage] = useState(10);
    const [count, setCount] = useState(0);
    const [search, setSearch] = useState('');

    const fetchCalculations = async () => {
        setLoading(true);
        try {
            // API использует пагинацию с 1, MUI с 0
            const data = await getCalculations(page + 1, rowsPerPage, search);
            setCalculations(data.results);
            setCount(data.count);
        } catch (error) {
            console.error("Failed to fetch calculations:", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchCalculations();
    }, [page, rowsPerPage, search]);

    const handleChangePage = (_event: unknown, newPage: number) => {
        setPage(newPage);
    };

    const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
        setRowsPerPage(parseInt(event.target.value, 10));
        setPage(0);
    };

    const handleDelete = async (id: number) => {
        if (window.confirm('Вы уверены, что хотите удалить этот расчёт?')) {
            try {
                await deleteCalculation(id);
                fetchCalculations();
            } catch (error) {
                console.error("Failed to delete:", error);
                alert("Ошибка при удалении");
            }
        }
    };

    return (
        <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
                <Typography variant="h4" component="h1" color="primary">
                    📊 Расчёты
                </Typography>
                <Button variant="contained" startIcon={<AddIcon />}>
                    Создать расчёт
                </Button>
            </Box>

            <Paper sx={{ p: 2, mb: 3 }}>
                <TextField
                    fullWidth
                    variant="outlined"
                    placeholder="Поиск расчёта..."
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                    InputProps={{
                        startAdornment: (
                            <InputAdornment position="start">
                                <SearchIcon />
                            </InputAdornment>
                        ),
                    }}
                />
            </Paper>

            <TableContainer component={Paper}>
                <Table sx={{ minWidth: 650 }} aria-label="simple table">
                    <TableHead sx={{ bgcolor: '#007bff' }}>
                        <TableRow>
                            <TableCell sx={{ color: 'white' }}>Название</TableCell>
                            <TableCell sx={{ color: 'white' }} align="center">Товаров</TableCell>
                            <TableCell sx={{ color: 'white' }} align="right">Сумма</TableCell>
                            <TableCell sx={{ color: 'white' }} align="right">С наценкой</TableCell>
                            <TableCell sx={{ color: 'white' }} align="right">Создан</TableCell>
                            <TableCell sx={{ color: 'white' }} align="center">Действия</TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {loading ? (
                            <TableRow>
                                <TableCell colSpan={6} align="center">Загрузка...</TableCell>
                            </TableRow>
                        ) : calculations.map((row) => (
                            <TableRow
                                key={row.id}
                                sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
                            >
                                <TableCell component="th" scope="row">
                                    {row.title}
                                </TableCell>
                                <TableCell align="center">{row.items_count}</TableCell>
                                <TableCell align="right">{Number(row.total_price).toFixed(2)} ₽</TableCell>
                                <TableCell align="right">{Number(row.total_price_with_markup).toFixed(2)} ₽</TableCell>
                                <TableCell align="right">
                                    {new Date(row.created_at).toLocaleDateString()}
                                </TableCell>
                                <TableCell align="center">
                                    <IconButton color="primary" size="small">
                                        <EditIcon />
                                    </IconButton>
                                    <IconButton color="error" size="small" onClick={() => handleDelete(row.id)}>
                                        <DeleteIcon />
                                    </IconButton>
                                </TableCell>
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
                <TablePagination
                    rowsPerPageOptions={[10, 25, 50]}
                    component="div"
                    count={count}
                    rowsPerPage={rowsPerPage}
                    page={page}
                    onPageChange={handleChangePage}
                    onRowsPerPageChange={handleChangeRowsPerPage}
                    labelRowsPerPage="На странице:"
                />
            </TableContainer>
        </Container>
    );
};

export default CalculationsPage;


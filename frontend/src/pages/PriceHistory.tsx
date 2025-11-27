
                  sx={{ color: 'white !important' }}
                >
                  Товар
                </TableSortLabel>
              </TableCell>
              <TableCell sx={{ color: 'white', fontWeight: 'bold' }} align="right">
                <TableSortLabel
                  active={orderBy === 'old_price'}
                  direction={orderDirection}
                  onClick={() => handleSort('old_price')}
                  sx={{ color: 'white !important' }}
                >
                  Старая цена
                </TableSortLabel>
              </TableCell>
              <TableCell sx={{ color: 'white', fontWeight: 'bold' }} align="right">
                <TableSortLabel
                  active={orderBy === 'new_price'}
                  direction={orderDirection}
                  onClick={() => handleSort('new_price')}
                  sx={{ color: 'white !important' }}
                >
                  Новая цена
                </TableSortLabel>
              </TableCell>
              <TableCell sx={{ color: 'white', fontWeight: 'bold' }} align="center">
                <TableSortLabel
                  active={orderBy === 'diff'}
                  direction={orderDirection}
                  onClick={() => handleSort('diff')}
                  sx={{ color: 'white !important' }}
                >
                  Изменение
                </TableSortLabel>
              </TableCell>
              <TableCell sx={{ color: 'white', fontWeight: 'bold' }} align="center">
                <TableSortLabel
                  active={orderBy === 'changed_at'}
                  direction={orderDirection}
                  onClick={() => handleSort('changed_at')}
                  sx={{ color: 'white !important' }}
                >
                  Дата
                </TableSortLabel>
              </TableCell>
              <TableCell sx={{ color: 'white', fontWeight: 'bold' }} align="center">
                <TableSortLabel
                  active={orderBy === 'changed_by_username'}
                  direction={orderDirection}
                  onClick={() => handleSort('changed_by_username')}
                  sx={{ color: 'white !important' }}
                >
                  Изменил
                </TableSortLabel>
              </TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {sortedResults.map((history: PriceHistory, index: number) => {
              const oldPrice = parseFloat(history.old_price);
              const newPrice = parseFloat(history.new_price);
              const diff = newPrice - oldPrice;
              const diffPercent = oldPrice > 0 ? ((diff / oldPrice) * 100).toFixed(1) : '0';

              return (
                <TableRow key={history.id} sx={{ '&:hover': { backgroundColor: '#f5f5f5' } }}>
                  <TableCell>{(page - 1) * 50 + index + 1}</TableCell>
                  <TableCell>
                    <Typography variant="body1" fontWeight="medium">
                      {history.item_name}
                    </Typography>
                  </TableCell>
                  <TableCell align="right">{oldPrice.toFixed(2)} ₽</TableCell>
                  <TableCell align="right">
                    <Typography variant="body1" fontWeight="bold">
                      {newPrice.toFixed(2)} ₽
                    </Typography>
                  </TableCell>
                  <TableCell align="center">
                    <Chip
                      icon={diff >= 0 ? <TrendingUpIcon /> : <TrendingDownIcon />}
                      label={`${diff >= 0 ? '+' : ''}${diff.toFixed(2)} ₽ (${diffPercent}%)`}
                      color={diff >= 0 ? 'success' : 'error'}
                      size="small"
                    />
                  </TableCell>
                  <TableCell align="center">
                    {new Date(history.changed_at).toLocaleDateString('ru-RU')}
                  </TableCell>
                  <TableCell align="center">
                    {history.changed_by_username || '-'}
                  </TableCell>
                </TableRow>
              );
            })}
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
          Всего записей: {data?.count || 0}
        </Typography>
      </Box>
    </Container>
  );
}

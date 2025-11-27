
                </TableCell>
                <TableCell align="center">
                  {new Date(snapshot.created_at).toLocaleDateString('ru-RU')}
                </TableCell>
                <TableCell align="center">
                  {snapshot.created_by_username || '-'}
                </TableCell>
                <TableCell align="center">
                  <Chip label={`${snapshot.items.length} товаров`} size="small" color="primary" variant="outlined" />
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
          Всего снимков: {data?.count || 0}
        </Typography>
      </Box>

      <Dialog
        open={!!selectedSnapshot}
        onClose={() => setSelectedSnapshot(null)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Typography variant="h6">Детали снимка: {selectedSnapshot?.calculation_title}</Typography>
            <IconButton onClick={() => setSelectedSnapshot(null)}>
              <CloseIcon />
            </IconButton>
          </Box>
        </DialogTitle>
        <DialogContent>
          {selectedSnapshot && (
            <Box>
              <Card sx={{ mb: 2 }}>
                <CardContent>
                  <Box display="flex" justifyContent="space-between" mb={1}>
                    <Typography>Стоимость без наценки:</Typography>
                    <Typography fontWeight="bold">
                      {parseFloat(selectedSnapshot.frozen_total_price).toFixed(2)} ₽
                    </Typography>
                  </Box>
                  <Box display="flex" justifyContent="space-between">
                    <Typography>Стоимость с наценкой:</Typography>
                    <Typography fontWeight="bold" color="primary">
                      {parseFloat(selectedSnapshot.frozen_total_price_with_markup).toFixed(2)} ₽
                    </Typography>
                  </Box>
                </CardContent>
              </Card>

              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Товар</TableCell>
                      <TableCell align="right">Цена</TableCell>
                      <TableCell align="center">Количество</TableCell>
                      <TableCell align="right">Итого</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {selectedSnapshot.items.map((item) => (
                      <TableRow key={item.id}>
                        <TableCell>{item.item_name}</TableCell>
                        <TableCell align="right">{parseFloat(item.item_price).toFixed(2)} ₽</TableCell>
                        <TableCell align="center">{item.quantity}</TableCell>
                        <TableCell align="right">{parseFloat(item.total_price).toFixed(2)} ₽</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </Box>
          )}
        </DialogContent>
      </Dialog>
    </Container>
  );
}

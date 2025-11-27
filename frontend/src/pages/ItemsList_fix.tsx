// Временный файл для исправления
// Нужно изменить:
// 1. Убрать setPage(1) из handleSearchChange (строка 129)
// 2. Добавить useEffect для сброса страницы после debounce

// В handleSearchChange:
const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
  const newValue = e.target.value;
  console.log('📝 Ввод:', newValue);
  setSearchInput(newValue);
  // УБРАТЬ: setPage(1); 
};

// После строки 56 (const debouncedSearch = useDebounce(searchInput, 500);) добавить:
useEffect(() => {
  setPage(1);
}, [debouncedSearch]);





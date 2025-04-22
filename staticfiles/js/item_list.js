document.addEventListener('DOMContentLoaded', () => {
  console.log("🟢 JS стартует");

  // === ПОИСК ===
  const searchInput = document.querySelector('#search-input');
  const clearButton = document.querySelector('#clear-search');
  const tableBody = document.querySelector('#item-table tbody');

  if (searchInput && clearButton && tableBody) {
    searchInput.addEventListener('input', () => {
      const searchTerm = searchInput.value.trim().toLowerCase();
      const rows = tableBody.querySelectorAll('tr');
      let found = false;

      rows.forEach(row => {
        const nameCell = row.querySelector('.item-name');
        const text = nameCell ? nameCell.textContent.trim().toLowerCase() : '';
        const match = text.includes(searchTerm);
        row.style.display = match ? '' : 'none';

        if (match && !found && searchTerm !== '') {
          row.scrollIntoView({behavior: 'smooth', block: 'center'});
          row.style.backgroundColor = '#d4edda';
          setTimeout(() => row.style.backgroundColor = '', 1500);
          found = true;
        }
      });
    });

    clearButton.addEventListener('click', () => {
      searchInput.value = '';
      searchInput.dispatchEvent(new Event('input'));
    });
  }

  // === СОРТИРОВКА ===
  const table = document.querySelector('#item-table');
  const headers = table.querySelectorAll('th.sortable');
  let sortDirection = 1;
  let activeColumn = 'name';

  const manualAlphabet = ' абвгдеёжзийклмнопрстуфхцчшщъыьэюяabcdefghijklmnopqrstuvwxyz0123456789';

  const normalizeForSort = (str) => {
    return str.toLowerCase()
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '')
      .replace(/[^\p{L}\p{N}]/gu, '');
  };

  const getManualSortKey = (text) => {
    const clean = normalizeForSort(text);
    return [...clean]
      .map(char => manualAlphabet.indexOf(char))
      .filter(index => index >= 0);
  };

  const sortTable = (column) => {
    const rows = Array.from(table.querySelectorAll('tbody tr'));

    if (activeColumn === column) {
      sortDirection *= -1;
    } else {
      activeColumn = column;
      sortDirection = 1;
    }

    headers.forEach(h => {
      const arrow = h.querySelector('.sort-arrow');
      if (arrow) arrow.textContent = '↕';
    });

    const arrow = document.querySelector(`th[data-sort="${column}"] .sort-arrow`);
    if (arrow) arrow.textContent = sortDirection === 1 ? '↑' : '↓';

    const getCellValue = (row) => {
      if (column === 'index') return parseInt(row.cells[0].textContent.trim());
      if (column === 'name') return row.cells[1].textContent;
      if (column === 'price') return parseFloat(row.cells[2].textContent.trim()) || 0;
    };

    rows.sort((a, b) => {
      const valA = getCellValue(a);
      const valB = getCellValue(b);
      console.log('🔍 Сравнение:', valA, 'vs', valB);

      if (typeof valA === 'string' && typeof valB === 'string') {
        const codeA = getManualSortKey(valA);
        const codeB = getManualSortKey(valB);

        for (let i = 0; i < Math.min(codeA.length, codeB.length); i++) {
          if (codeA[i] !== codeB[i]) {
            return (codeA[i] - codeB[i]) * sortDirection;
          }
        }
        return (codeA.length - codeB.length) * sortDirection;
      }

      return (valA - valB) * sortDirection;
    });

    const tbody = table.querySelector('tbody');
    tbody.innerHTML = '';
    rows.forEach(row => tbody.appendChild(row));
  };

  headers.forEach(header => {
    header.addEventListener('click', () => {
      const column = header.getAttribute('data-sort');
      sortTable(column);
    });
  });

  // 🚀 Автосортировка
  sortTable('name');
  console.log("🚀 Автосортировка по name запущена");
});

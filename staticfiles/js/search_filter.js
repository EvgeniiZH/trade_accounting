document.addEventListener('DOMContentLoaded', () => {
  const searchInput = document.querySelector('#search-input');
  const clearButton = document.querySelector('#clear-search');
  const tableBody = document.querySelector('#item-table tbody');

  if (!searchInput || !tableBody) return;

  const highlightMatch = (text, term) => {
    const escaped = term.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); // экранируем спецсимволы
    const regex = new RegExp(`(${escaped})`, 'gi');
    return text.replace(regex, '<mark>$1</mark>');
  };

  const filterTable = () => {
    const searchTerm = searchInput.value.trim().toLowerCase();
    const rows = tableBody.querySelectorAll('tr');
    let found = false;

    rows.forEach(row => {
      const nameCell = row.querySelector('.item-name');
      const originalText = nameCell?.textContent || '';
      const text = originalText.trim().toLowerCase();
      const match = text.includes(searchTerm);

      row.style.display = match ? '' : 'none';

      if (nameCell) {
        nameCell.innerHTML = match && searchTerm !== ''
          ? highlightMatch(originalText, searchTerm)
          : originalText;
      }

      if (match && !found && searchTerm !== '') {
        // row.scrollIntoView({ behavior: 'smooth', block: 'center' }); // ⛔ отключаем резкую прокрутку
        row.style.backgroundColor = '#d4edda';
        setTimeout(() => row.style.backgroundColor = '', 1000);
        found = true;
      }
    });
  };

  searchInput.addEventListener('input', filterTable);

  if (clearButton) {
    clearButton.addEventListener('click', () => {
      searchInput.value = '';
      filterTable();
    });
  }
});

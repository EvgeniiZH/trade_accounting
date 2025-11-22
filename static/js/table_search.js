const initTableSearch = (container) => {
  const tableId = container.dataset.tableId;
  const table = tableId ? document.getElementById(tableId) : null;
  if (!table) return;

  const searchInput = container.querySelector('[data-role="search-input"]');
  const clearButton = container.querySelector('[data-role="clear-search"]');
  if (!searchInput) return;

  const rowSelector = container.dataset.rowSelector || 'tbody tr';
  const cellSelector = container.dataset.cellSelector || '.search-target';

  const getCells = (row) => {
    if (!cellSelector) return [row];
    const cells = row.querySelectorAll(cellSelector);
    return cells.length ? Array.from(cells) : [row];
  };

  const rows = Array.from(table.querySelectorAll(rowSelector));
  rows.forEach((row) => {
    getCells(row).forEach((cell) => {
      if (!cell.dataset.original) {
        cell.dataset.original = cell.innerHTML.trim();
      }
    });
  });

  const highlightText = (cell, term) => {
    const original = cell.dataset.original ?? cell.innerHTML;
    if (!term) {
      cell.innerHTML = original;
      return;
    }
    try {
      const escaped = term.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
      const regex = new RegExp(`(${escaped})`, 'gi');
      cell.innerHTML = original.replace(regex, '<mark>$1</mark>');
    } catch (err) {
      cell.innerHTML = original;
    }
  };

  const filterRows = () => {
    const term = searchInput.value.trim().toLowerCase();
    let firstMatch = null;

    rows.forEach((row) => {
      const cells = getCells(row);
      const text = cells
        .map((cell) => (cell.dataset.original ?? cell.innerText ?? '').trim().toLowerCase())
        .join(' ');
      const match = term === '' || text.includes(term);

      row.style.display = match ? '' : 'none';

      cells.forEach((cell) => highlightText(cell, match && term ? term : ''));

      if (match && !firstMatch && term) {
        firstMatch = row;
      }

      if (!match) {
        row.classList.remove('search-hit');
      }
    });

    if (firstMatch) {
      firstMatch.classList.add('search-hit');
      setTimeout(() => firstMatch.classList.remove('search-hit'), 1200);
    }
  };

  searchInput.addEventListener('input', filterRows);

  if (clearButton) {
    clearButton.addEventListener('click', () => {
      searchInput.value = '';
      filterRows();
      searchInput.focus();
    });
  }

  filterRows();
};

const registerFocusHotkey = () => {
  document.addEventListener('keydown', (event) => {
    if (
      event.key !== '/' ||
      event.defaultPrevented ||
      event.metaKey ||
      event.ctrlKey ||
      event.altKey ||
      event.target.matches('input, textarea') ||
      event.target.isContentEditable
    ) {
      return;
    }
    const target = document.querySelector('[data-focus-hotkey="/"]');
    if (target) {
      event.preventDefault();
      target.focus();
      target.select?.();
    }
  });
};

document.addEventListener('DOMContentLoaded', () => {
  const containers = document.querySelectorAll('[data-table-search]');
  if (containers.length === 0) return;

  registerFocusHotkey();
  containers.forEach(initTableSearch);
});

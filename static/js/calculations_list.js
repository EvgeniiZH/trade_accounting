document.addEventListener('DOMContentLoaded', () => {
  const table = document.querySelector('#calculation-table');
  const searchInput = document.querySelector('#search-input');
  const clearBtn = document.querySelector('#clear-search');
  const selectAll = document.querySelector('#select_all');
  const checkboxes = document.querySelectorAll("input[name='calc_ids']");

  // === Поиск
  if (table && searchInput && clearBtn) {
    const tableRows = table.querySelectorAll('tbody tr');

    const filterRows = () => {
      const term = searchInput.value.trim().toLowerCase();
      tableRows.forEach(row => {
        const titleCell = row.querySelector('.calc-title');
        const text = titleCell ? titleCell.textContent.trim().toLowerCase() : '';
        const match = text.includes(term);
        row.style.display = match ? '' : 'none';

        if (match && term !== '') {
          row.style.backgroundColor = '#d4edda';
          setTimeout(() => row.style.backgroundColor = '', 1000);
        }
      });
    };

    searchInput.addEventListener('input', filterRows);
    clearBtn.addEventListener('click', () => {
      searchInput.value = '';
      filterRows();
    });

    filterRows();
  }

  // === Выбор всех
  if (selectAll && checkboxes.length > 0) {
    selectAll.addEventListener('change', () => {
      checkboxes.forEach(cb => (cb.checked = selectAll.checked));
    });
  }

  // === Прокрутка к обновлённому или новому расчёту
  const params = new URLSearchParams(window.location.search);
  const updatedCalcId = params.get('updated_calc') || params.get('new_calc');

  if (updatedCalcId) {
    const row = document.getElementById(`calc-${updatedCalcId}`);
    if (row) {
      row.scrollIntoView({ behavior: 'smooth', block: 'center' });
      row.classList.add('table-success');
      setTimeout(() => {
        row.classList.remove('table-success');
      }, 3000);
    }
  }
    // === Подтверждение удаления расчёта
  const deleteButtons = document.querySelectorAll('button[name="delete_calc"]');

  deleteButtons.forEach(btn => {
    btn.addEventListener('click', (e) => {
      const row = btn.closest('tr');
      const title = row?.querySelector('.calc-title')?.textContent.trim() || 'этот расчёт';
      const confirmed = confirm(`Вы действительно хотите удалить расчёт: «${title}»?`);

      if (!confirmed) {
        e.preventDefault(); // отменить отправку формы
      }
    });
  });

});

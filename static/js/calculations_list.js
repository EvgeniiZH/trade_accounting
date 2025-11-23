document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.querySelector('#search-input');
    const clearButton = document.querySelector('#clear-search');
    const container = document.querySelector('#calculations-list-container');
    
    let searchTimeout;

    // === Loader ===
    function toggleLoader(show) {
        const loader = document.querySelector('.table-loader');
        if (loader) {
            if (show) loader.classList.add('active');
            else loader.classList.remove('active');
        }
    }

    // === Инициализация событий (вызывать после AJAX) ===
    function initEvents() {
        if (!container) return;

        // Делегирование кликов на контейнере (для сортировки и пагинации)
        // Мы не удаляем старые обработчики, так как контейнер перерисовывается полностью
        // Но лучше вешать на сам container один раз (см. ниже)
        
        const tableBody = container.querySelector('tbody');
        if (tableBody) {
            // === Подтверждение удаления ===
            const deleteButtons = tableBody.querySelectorAll('button[name="delete_calc"]');
            deleteButtons.forEach(btn => {
                btn.addEventListener('click', (e) => {
                    const row = btn.closest('tr');
                    const title = row?.querySelector('.calc-title')?.textContent.trim() || 'этот расчёт';
                    const confirmed = confirm(`Вы действительно хотите удалить расчёт: «${title}»?`);
                    if (!confirmed) {
                        e.preventDefault();
                    }
                });
            });
        }

        // === Select All ===
        const selectAll = container.querySelector('#select_all');
        if (selectAll) {
            selectAll.addEventListener('change', () => {
                const checkboxes = container.querySelectorAll("input[name='calc_ids']");
                checkboxes.forEach(cb => (cb.checked = selectAll.checked));
            });
        }
    }

    // === AJAX Запрос ===
    function fetchData(url) {
        toggleLoader(true);
        
        fetch(url, { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
        .then(response => response.text())
        .then(html => {
            if (container) {
                container.innerHTML = html;
                initEvents();
                window.history.pushState({}, '', url);
                
                // Подсветка
                const searchTerm = url.searchParams.get('search');
                if (searchTerm) highlightSearch(searchTerm);
            }
        })
        .catch(err => console.error('Error:', err))
        .finally(() => toggleLoader(false));
    }

    // === Поиск ===
    function performSearch() {
        const searchTerm = searchInput.value.trim();
        const url = new URL(window.location.href);
        url.searchParams.set('search', searchTerm);
        if (searchTerm !== (url.searchParams.get('search') || '')) {
             url.searchParams.set('page', 1);
        }
        fetchData(url);
    }

    // === Подсветка ===
    function highlightSearch(term) {
        if (!term) return;
        const tableBody = container.querySelector('tbody');
        if (!tableBody) return;

        term = term.toLowerCase();
        tableBody.querySelectorAll('.calc-title a').forEach(cell => {
            if (cell.textContent.toLowerCase().includes(term)) {
                const regex = new RegExp(`(${term.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
                cell.innerHTML = cell.textContent.replace(regex, '<mark>$1</mark>');
                cell.closest('tr').classList.add('search-hit');
                setTimeout(() => cell.closest('tr').classList.remove('search-hit'), 3000);
            }
        });
        
        const firstMatch = tableBody.querySelector('.search-hit');
        if (firstMatch) firstMatch.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }

    // === Глобальный слушатель кликов (для пагинации и сортировки) ===
    if (container) {
        container.addEventListener('click', (e) => {
            const link = e.target.closest('a.page-link, a.sort-link');
            if (link) {
                e.preventDefault();
                const url = new URL(link.getAttribute('href'), window.location.href);
                // Сохраняем текущий поиск
                const currentSearch = searchInput.value.trim();
                if (currentSearch) url.searchParams.set('search', currentSearch);
                
                fetchData(url);
            }
        });
    }

    if (searchInput) {
        searchInput.addEventListener('input', () => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(performSearch, 1000);
        });

        searchInput.addEventListener('keydown', (event) => {
            if (event.key === 'Enter') {
                event.preventDefault();
                clearTimeout(searchTimeout);
                performSearch();
            }
        });
        
        document.addEventListener('keydown', (event) => {
            if (event.key === '/' && document.activeElement !== searchInput) {
                event.preventDefault();
                searchInput.focus();
            }
        });
    }

    if (clearButton) {
        clearButton.addEventListener('click', () => {
            searchInput.value = '';
            performSearch();
            searchInput.focus();
        });
    }

    // Инициализация при загрузке
    initEvents();

    // === Прокрутка к обновлённому (только при загрузке) ===
    const params = new URLSearchParams(window.location.search);
    const updatedCalcId = params.get('updated_calc') || params.get('new_calc');
    if (updatedCalcId) {
        const row = document.getElementById(`calc-${updatedCalcId}`);
        if (row) {
            row.scrollIntoView({ behavior: 'smooth', block: 'center' });
            row.classList.add('table-success');
            setTimeout(() => row.classList.remove('table-success'), 3000);
        }
    }
});
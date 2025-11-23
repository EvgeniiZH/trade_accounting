document.addEventListener('DOMContentLoaded', () => {
    // Ссылки на элементы формы (они вне контейнера обновления)
    const markupInput = document.querySelector('#markup');
    const totalWithout = document.querySelector('#total-without-markup');
    const totalWith = document.querySelector('#total-with-markup');
    const searchInput = document.querySelector('#search-input');
    const clearButton = document.querySelector('#clear-search');
    let filterButton = null;
    let filterActive = false;
    const selectedItemsContainer = document.querySelector('#selected-items-container');
    const form = document.querySelector('#create-calc-form');
    
    // Контейнер, который мы будем обновлять
    const container = document.querySelector('#create-calculation-container');
    
    let searchTimeout;

    // Хранилище состояния
    const selectedState = {
        items: new Set(), // Set of IDs
        quantities: new Map(), // Map: ID -> Quantity
        prices: new Map() // Map: ID -> Price
    };

    // === Loader ===
    function toggleLoader(show) {
        const loader = document.querySelector('.table-loader');
        if (loader) {
            if (show) loader.classList.add('active');
            else loader.classList.remove('active');
        }
    }

    // === Инициализация состояния из текущей таблицы (при загрузке) ===
    function initState() {
        if (!container) return;
        const tableBody = container.querySelector('tbody');
        if (!tableBody) return;
        
        const rows = tableBody.querySelectorAll('tr');
        rows.forEach(row => {
            const checkbox = row.querySelector('.item-checkbox');
            const quantityInput = row.querySelector('.quantity-input');
            const priceCell = row.querySelector('.item-price');
            const itemId = checkbox.value;
            const price = parseFloat(priceCell.textContent.replace(/\s|₽/g, '')) || 0;
            
            selectedState.prices.set(itemId, price);

            if (checkbox.checked) {
                selectedState.items.add(itemId);
                selectedState.quantities.set(itemId, quantityInput.value);
            }
        });
        
        syncHiddenInputs();
        recalculateTotals();
    }

    // === Синхронизация скрытых инпутов ===
    function syncHiddenInputs() {
        if (!selectedItemsContainer) return;
        selectedItemsContainer.innerHTML = '';

        selectedState.items.forEach(itemId => {
            const inputId = document.createElement('input');
            inputId.type = 'hidden';
            inputId.name = 'items';
            inputId.value = itemId;
            selectedItemsContainer.appendChild(inputId);

            const qty = selectedState.quantities.get(itemId) || '1';
            const inputQty = document.createElement('input');
            inputQty.type = 'hidden';
            inputQty.name = `quantity_${itemId}`;
            inputQty.value = qty;
            selectedItemsContainer.appendChild(inputQty);
        });
    }

    // === Инициализация событий (вызывать после AJAX) ===
    function initEvents() {
        if (!container) return;
        const tableBody = container.querySelector('tbody');
        
        // Восстанавливаем состояние и вешаем обработчики
        if (tableBody) {
            const rows = tableBody.querySelectorAll('tr');
        rows.forEach(row => {
            const checkbox = row.querySelector('.item-checkbox');
                const quantityInput = row.querySelector('.quantity-input');
                const priceCell = row.querySelector('.item-price');
                const itemId = checkbox.value;
                const price = parseFloat(priceCell.textContent.replace(/\s|₽/g, '')) || 0;
                
                selectedState.prices.set(itemId, price);

                if (selectedState.items.has(itemId)) {
                    checkbox.checked = true;
                    if (selectedState.quantities.has(itemId)) {
                        quantityInput.value = selectedState.quantities.get(itemId);
                    }
                    row.classList.add('highlighted');
                } else {
                    checkbox.checked = false;
                    row.classList.remove('highlighted');
                }

                // События строки
                checkbox.addEventListener('change', () => {
                    if (checkbox.checked) {
                        selectedState.items.add(itemId);
                        selectedState.quantities.set(itemId, quantityInput.value);
                        row.classList.add('highlighted');
                    } else {
                        selectedState.items.delete(itemId);
                        selectedState.quantities.delete(itemId);
                        row.classList.remove('highlighted');
                    }
                    syncHiddenInputs();
                    recalculateTotals();
                    
                    if (filterActive) applyFilterOnlySelected();
                });

                quantityInput.addEventListener('input', () => {
                    if (selectedState.items.has(itemId)) {
                        selectedState.quantities.set(itemId, quantityInput.value);
                        syncHiddenInputs();
                        recalculateTotals();
                    }
                });
            });
        }

        // Кнопка фильтра
        filterButton = container.querySelector('#filter-selected');
        if (filterButton) {
            filterButton.addEventListener('click', () => {
                filterActive = !filterActive;
                updateFilterButton();
                applyFilterOnlySelected();
            });
            updateFilterButton();
            if (filterActive) applyFilterOnlySelected();
        }
    }

    // === Глобальный слушатель кликов на контейнере ===
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

    // === AJAX Запрос ===
    function fetchData(url) {
        toggleLoader(true);
        
        fetch(url, { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
        .then(response => response.text())
        .then(html => {
            if (container) {
                container.innerHTML = html;
                initEvents(); // Восстанавливаем состояние
                window.history.pushState({}, '', url);
                
                // Подсветка
                const searchTerm = url.searchParams.get('search');
                if (searchTerm) {
                    const term = searchTerm.toLowerCase();
                    const tableBody = container.querySelector('tbody');
                    if (tableBody) {
                        let firstMatch = null;
                        tableBody.querySelectorAll('.item-name').forEach(cell => {
                            if (cell.textContent.toLowerCase().includes(term)) {
                                const regex = new RegExp(`(${term.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
                                cell.innerHTML = cell.textContent.replace(regex, '<mark>$1</mark>');
                                const row = cell.closest('tr');
                                row.classList.add('search-hit');
                                setTimeout(() => row.classList.remove('search-hit'), 3000);
                                if (!firstMatch) firstMatch = row;
                            }
                        });
                        if (firstMatch) firstMatch.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    }
                }
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

    // === Пересчет итогов ===
    function recalculateTotals() {
        let total = 0;
        selectedState.items.forEach(itemId => {
            const price = selectedState.prices.get(itemId) || 0;
            const qty = parseInt(selectedState.quantities.get(itemId) || '1', 10);
            total += price * qty;
        });

        const markup = parseFloat(markupInput.value || '0') || 0;
        const totalWithMarkup = total * (1 + markup / 100);

        totalWithout.textContent = total.toFixed(2) + ' ₽';
        totalWith.textContent = totalWithMarkup.toFixed(2) + ' ₽';
    }

    if (markupInput) {
        markupInput.addEventListener('input', recalculateTotals);
    }

    // === Фильтр ===
    function applyFilterOnlySelected() {
        const tableBody = container?.querySelector('tbody');
        if (!tableBody) return;
        const rows = tableBody.querySelectorAll('tr');
            rows.forEach(row => {
            const checkbox = row.querySelector('.item-checkbox');
            const shouldShow = checkbox.checked || !filterActive;
            row.style.display = shouldShow ? '' : 'none';
        });
    }

    function updateFilterButton() {
        if (!filterButton) return;
        filterButton.dataset.active = String(filterActive);
        filterButton.textContent = filterActive ? '🔄 Показать все' : '🔘 Показать только выбранные';
        filterButton.classList.toggle('btn-secondary', filterActive);
        filterButton.classList.toggle('btn-outline-secondary', !filterActive);
    }

    // Форма
    if (form) {
        form.addEventListener('submit', () => {
            const tableCheckboxes = form.querySelectorAll('table input[name="items"]');
            tableCheckboxes.forEach(cb => cb.removeAttribute('name'));
            const tableQuantities = form.querySelectorAll('table input[name^="quantity_"]');
            tableQuantities.forEach(qty => qty.removeAttribute('name'));
        });
    }

    // Запуск
    initState();
    initEvents();
});
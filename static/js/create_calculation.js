document.addEventListener('DOMContentLoaded', () => {
    // Ссылки на элементы формы (они вне контейнера обновления)
    const markupInput = document.querySelector('#markup');
    const totalWithout = document.querySelector('#total-without-markup');
    const totalWith = document.querySelector('#total-with-markup');
    const searchInput = document.querySelector('#search-input');
    const clearButton = document.querySelector('#clear-search');
    let filterButton = document.querySelector('#filter-selected');
    let filterActive = false;
    const selectedItemsContainer = document.querySelector('#selected-items-container');
    const form = document.querySelector('#create-calc-form');
    const DEBOUNCE_DELAY = 500;
    
    // Контейнер, который мы будем обновлять (только таблица)
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
        if (!container) return;
        const loader = container.querySelector('.table-loader');
        if (loader) {
            loader.classList.toggle('active', Boolean(show));
        }
    }

    function applySearchParam(url, searchTerm) {
        const previousSearch = url.searchParams.get('search') || '';
        
        // Сохраняем page_size перед изменениями
        const currentPageSize = new URLSearchParams(window.location.search).get('page_size');
        if (currentPageSize) {
            url.searchParams.set('page_size', currentPageSize);
        }
        
        if (searchTerm) {
            url.searchParams.set('search', searchTerm);
        } else {
            url.searchParams.delete('search');
        }
        if (searchTerm !== previousSearch) {
            url.searchParams.set('page', 1);
        }
        return url;
    }

    function highlightSearch(term) {
        const tableBody = container?.querySelector('tbody');
        if (!tableBody) return;

        const normalizedTerm = term?.toLowerCase() || '';
        let firstMatch = null;

        tableBody.querySelectorAll('.item-name').forEach(cell => {
            const rawText = cell.dataset.rawText || cell.textContent;
            cell.dataset.rawText = rawText;
            const row = cell.closest('tr');
            row?.classList.remove('search-hit');

            if (!normalizedTerm) {
                cell.innerHTML = rawText;
                return;
            }

            if (rawText.toLowerCase().includes(normalizedTerm)) {
                const regex = new RegExp(`(${normalizedTerm.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
                cell.innerHTML = rawText.replace(regex, '<mark>$1</mark>');
                row?.classList.add('search-hit');
                if (!firstMatch) firstMatch = row;
                setTimeout(() => row?.classList.remove('search-hit'), 2000);
            } else {
                cell.innerHTML = rawText;
            }
        });

        if (firstMatch) {
            firstMatch.scrollIntoView({ behavior: 'smooth', block: 'center' });
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

        // Кнопка фильтра обновляется, если она внутри контейнера (на случай если переместим обратно)
        // Но сейчас она вне контейнера, так что обработчик уже установлен
    }

    // === События поиска (поле теперь вне контейнера) ===
    if (searchInput) {
        searchInput.addEventListener('input', () => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(performSearch, DEBOUNCE_DELAY);
        });

        searchInput.addEventListener('keydown', (event) => {
            if (event.key === 'Enter') {
                event.preventDefault();
                clearTimeout(searchTimeout);
                performSearch();
            }
        });
    }

    if (clearButton) {
        clearButton.addEventListener('click', () => {
            if (searchInput) {
                searchInput.value = '';
                performSearch();
                searchInput.focus();
            }
        });
    }

    // === Глобальный слушатель кликов на контейнере (пагинация, сортировка) ===
    if (container) {
        container.addEventListener('click', (e) => {
            const link = e.target.closest('a.page-link, a.sort-link');
            if (!link) return;
            e.preventDefault();
            const url = new URL(link.getAttribute('href'), window.location.href);
            const currentSearch = searchInput?.value.trim();
            if (currentSearch) {
                url.searchParams.set('search', currentSearch);
            } else {
                url.searchParams.delete('search');
            }
            fetchData(url);
        });
    }

    // === Применение стилей к таблице ===
    function applyTableStyles() {
        // Используем более специфичный селектор для перебития calculations_list.css
        const wrapper = document.querySelector('#create-calculation-wrapper');
        if (!wrapper) {
            setTimeout(applyTableStyles, 100);
            return;
        }
        
        const table = wrapper.querySelector('#calculation-table');
        if (!table) {
            // Если таблица ещё не загружена, попробуем ещё раз через небольшую задержку
            setTimeout(applyTableStyles, 100);
            return;
        }
        
        // Применяем стили напрямую к таблице с !important
        table.style.setProperty('table-layout', 'auto', 'important');
        table.style.setProperty('width', '100%', 'important');
        table.style.setProperty('overflow', 'visible', 'important');
        
        // Применяем стили к колонкам - убираем фиксированные ширины для автоматического распределения
        const cols = [
            { nth: 1, align: 'center' },
            { nth: 2, align: 'left', wrap: true },
            { nth: 3, align: 'right' },
            { nth: 4, align: 'center' },
            { nth: 5, align: 'center' }
        ];
        
        cols.forEach(col => {
            const ths = table.querySelectorAll(`thead th:nth-child(${col.nth})`);
            const tds = table.querySelectorAll(`tbody td:nth-child(${col.nth})`);
            [...ths, ...tds].forEach(el => {
                // Убираем фиксированные ширины - пусть таблица сама распределяет
                el.style.removeProperty('width');
                el.style.removeProperty('min-width');
                el.style.setProperty('text-align', col.align, 'important');
                if (col.wrap) {
                    el.style.setProperty('white-space', 'normal', 'important');
                    el.style.setProperty('overflow-wrap', 'anywhere', 'important');
                }
            });
        });
    }

    // === AJAX Запрос ===
    function fetchData(url) {
        toggleLoader(true);
        
        fetch(url.toString(), { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
        .then(response => response.text())
        .then(html => {
            if (container) {
                container.innerHTML = html;
                applyTableStyles(); // Применяем стили после обновления
                initEvents(); // Восстанавливаем состояние
                window.history.pushState({}, '', url.toString());
                highlightSearch(url.searchParams.get('search'));
            }
        })
        .catch(err => console.error('Error:', err))
        .finally(() => toggleLoader(false));
    }

    // === Поиск ===
    function performSearch() {
        if (!searchInput) return;
        const searchTerm = searchInput.value.trim();
        const url = applySearchParam(new URL(window.location.href), searchTerm);
        fetchData(url);
    }

    // === Hotkey для фокуса на поиск ===
    document.addEventListener('keydown', (event) => {
        if (event.key === '/' && searchInput && document.activeElement !== searchInput) {
            event.preventDefault();
            searchInput.focus();
        }
    });

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

    // === Инициализация кнопки фильтра (она теперь вне AJAX-контейнера) ===
    if (filterButton) {
        filterButton.addEventListener('click', () => {
            filterActive = !filterActive;
            updateFilterButton();
            applyFilterOnlySelected();
        });
        updateFilterButton();
    }

    // Запуск
    initState();
    initEvents();
    
    // Применяем стили при загрузке страницы (несколько раз для надёжности)
    applyTableStyles();
    requestAnimationFrame(() => {
        applyTableStyles();
        setTimeout(applyTableStyles, 100);
        setTimeout(applyTableStyles, 500);
    });
});
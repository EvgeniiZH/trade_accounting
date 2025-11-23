document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.querySelector('#search-input');
    const clearButton = document.querySelector('#clear-search');
    const container = document.querySelector('#item-list-container');
    
    let searchTimeout;

    // === Loader ===
    function toggleLoader(show) {
        const loader = document.querySelector('.table-loader');
        if (loader) {
            if (show) loader.classList.add('active');
            else loader.classList.remove('active');
        }
    }

    // === Инициализация событий (сортировка, пагинация) ===
    function initEvents() {
        if (!container) return;

        // Сортировка и Пагинация (делегирование)
        container.addEventListener('click', (e) => {
            const link = e.target.closest('a.page-link, a.sort-link');
            if (link) {
                e.preventDefault();
                const url = new URL(link.getAttribute('href'), window.location.href);
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
                // initEvents не нужно вызывать заново, так как мы используем делегирование на container,
                // который не меняется (меняется его содержимое). 
                // А стоп, container.innerHTML меняет всё внутри.
                // Делегирование работает, если обработчик висит на самом container.
                // Так что всё ок.
                
                // Обновляем URL
                window.history.pushState({}, '', url);
                
                // Подсветка поиска
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
             url.searchParams.set('page', 1); // Сброс на 1 страницу при новом поиске
        }
        fetchData(url);
    }

    // === Подсветка ===
    function highlightSearch(term) {
        if (!term) return;
        const tableBody = document.querySelector('#item-table tbody');
        if (!tableBody) return;

        term = term.toLowerCase();
        tableBody.querySelectorAll('.item-name').forEach(cell => {
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

    // Инициализация
    initEvents();
});
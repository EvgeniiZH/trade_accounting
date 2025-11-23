document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.querySelector('#search-input');
    const clearButton = document.querySelector('#clear-search');
    const container = document.querySelector('#item-list-container');
    const DEBOUNCE_DELAY = 500;
    let searchTimeout;

    function toggleLoader(show) {
        if (!container) return;
        const loader = container.querySelector('.table-loader');
        if (loader) {
            loader.classList.toggle('active', Boolean(show));
        }
    }

    function applySearchParam(url, searchTerm) {
        const previousSearch = url.searchParams.get('search') || '';
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
        const tableBody = container?.querySelector('#item-table tbody');
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

    function fetchData(url) {
        toggleLoader(true);
        fetch(url.toString(), { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
            .then(response => response.text())
            .then(html => {
                if (!container) return;
                container.innerHTML = html;
                window.history.pushState({}, '', url.toString());
                highlightSearch(url.searchParams.get('search'));
            })
            .catch(err => console.error('Error:', err))
            .finally(() => toggleLoader(false));
    }

    function performSearch() {
        if (!searchInput) return;
        const searchTerm = searchInput.value.trim();
        const url = applySearchParam(new URL(window.location.href), searchTerm);
        fetchData(url);
    }

    function initEvents() {
        if (!container) return;
        container.addEventListener('click', (e) => {
            const link = e.target.closest('a.page-link, a.sort-link');
            if (!link) return;
            e.preventDefault();
            const url = new URL(link.getAttribute('href'), window.location.href);
            const currentSearch = searchInput?.value.trim();
            if (typeof currentSearch === 'string' && currentSearch.length) {
                url.searchParams.set('search', currentSearch);
            }
            fetchData(url);
        });
    }

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

        document.addEventListener('keydown', (event) => {
            if (event.key === '/' && document.activeElement !== searchInput) {
                event.preventDefault();
                searchInput.focus();
            }
        });
    }

    if (clearButton) {
        clearButton.addEventListener('click', () => {
            if (!searchInput) return;
            searchInput.value = '';
            performSearch();
            searchInput.focus();
        });
    }

    initEvents();
});
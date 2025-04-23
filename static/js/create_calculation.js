console.log('Поиск активирован!');

document.addEventListener('DOMContentLoaded', () => {
    const table = document.querySelector('#calculation-table');
    const markupInput = document.querySelector('#markup');
    const totalWithout = document.querySelector('#total-without-markup');
    const totalWith = document.querySelector('#total-with-markup');
    const searchInput = document.querySelector('#search-input');
    const clearButton = document.querySelector('#clear-search');
    const calcTableBody = table?.querySelector('tbody');

    function recalculateTotals() {
        if (!table || !markupInput || !totalWithout || !totalWith) return;

        let total = 0;

        calcTableBody.querySelectorAll('tr').forEach(row => {
            const checkbox = row.querySelector('.item-checkbox');
            const priceCell = row.querySelector('.item-price');
            const quantityInput = row.querySelector('.quantity-input');

            const price = parseFloat(priceCell?.textContent || '0') || 0;
            const quantity = parseInt(quantityInput?.value || '1') || 0;

            const rowTotal = price * quantity;
            const isChecked = checkbox?.checked;

            if (isChecked) total += rowTotal;
            row.classList.toggle('highlighted', isChecked);
        });

        const markup = parseFloat(markupInput.value || '0') || 0;
        const totalWithMarkup = total * (1 + markup / 100);

        totalWithout.textContent = total.toFixed(2) + ' ₽';
        totalWith.textContent = totalWithMarkup.toFixed(2) + ' ₽';
    }

    if (table) {
        table.addEventListener('input', recalculateTotals);
        table.addEventListener('change', recalculateTotals);
        markupInput.addEventListener('input', recalculateTotals);
        table.querySelectorAll('.item-checkbox').forEach(cb => {
            cb.addEventListener('change', recalculateTotals);
        });
        recalculateTotals();
    }

    // === Поиск + подсветка ===
    if (searchInput && clearButton && calcTableBody) {
        searchInput.addEventListener('input', () => {
            const searchTerm = searchInput.value.trim().toLowerCase();
            const rows = calcTableBody.querySelectorAll('tr');
            let found = false;

            rows.forEach(row => {
                const nameCell = row.querySelector('.item-name');
                if (!nameCell) return;

                const originalText = nameCell.getAttribute('data-original') || nameCell.textContent.trim();
                const lowerOriginal = originalText.toLowerCase();
                const match = lowerOriginal.includes(searchTerm);

                row.style.display = match ? '' : 'none';

                if (match && searchTerm) {
                    const regex = new RegExp(`(${searchTerm})`, 'gi');
                    nameCell.innerHTML = originalText.replace(regex, '<mark>$1</mark>');
                } else {
                    nameCell.innerHTML = originalText;
                }

                nameCell.setAttribute('data-original', originalText);

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
});

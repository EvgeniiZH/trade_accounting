document.addEventListener('DOMContentLoaded', () => {
    const table = document.querySelector('#calculation-table');
    const markupInput = document.querySelector('#markup');
    const totalWithout = document.querySelector('#total-without-markup');
    const totalWith = document.querySelector('#total-with-markup');

    function recalculateTotals() {
        if (!table || !markupInput || !totalWithout || !totalWith) return;

        let total = 0;

        table.querySelectorAll('tbody tr').forEach(row => {
            const checkbox = row.querySelector('.item-checkbox');
            const priceCell = row.querySelector('.item-price');
            const quantityInput = row.querySelector('.quantity-input');

            const price = parseFloat(priceCell?.textContent || '0') || 0;
            const quantity = parseInt(quantityInput?.value || '1') || 0;

            const rowTotal = price * quantity;

            const isChecked = checkbox?.checked;

            if (isChecked) {
                total += rowTotal;
            }

            // Подсветка строки при включённом чекбоксе
            row.classList.toggle('highlighted', isChecked);
        });

        const markup = parseFloat(markupInput.value || '0') || 0;
        const totalWithMarkup = total * (1 + markup / 100);

        totalWithout.textContent = total.toFixed(2) + ' ₽';
        totalWith.textContent = totalWithMarkup.toFixed(2) + ' ₽';
    }

    table.addEventListener('input', recalculateTotals);
    table.addEventListener('change', recalculateTotals);
    markupInput.addEventListener('input', recalculateTotals);

    // Отдельно — на каждую галочку при загрузке
    table.querySelectorAll('.item-checkbox').forEach(cb => {
        cb.addEventListener('change', recalculateTotals);
    });

    recalculateTotals();
});

document.addEventListener('DOMContentLoaded', () => {
    // Определяем, какая таблица используется: товары (item-table) или расчёты (calculation-table)
    const itemTable = document.getElementById('item-table');
    const calculationTable = document.getElementById('calculation-table');
    let tableBody = null;
    let isItemTable = false;
    if (itemTable) {
        tableBody = itemTable.querySelector('tbody');
        isItemTable = true;
    } else if (calculationTable) {
        tableBody = calculationTable.querySelector('tbody');
    }

    // ===== AJAX для обновления товара (только для таблицы товаров) =====
    if (isItemTable) {
        document.querySelectorAll('button[name="edit_item"]').forEach(button => {
            button.addEventListener('click', function (event) {
                event.preventDefault(); // Отменяем стандартное поведение формы

                const itemId = this.value;
                const row = document.getElementById(`item-${itemId}`);
                const nameField = row.querySelector(`textarea[name="name_${itemId}"]`);
                const priceField = row.querySelector(`input[name="price_${itemId}"]`);
                const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

                const params = new URLSearchParams();
                params.append('edit_item', itemId);
                params.append(`name_${itemId}`, nameField.value);
                params.append(`price_${itemId}`, priceField.value);

                fetch('/ajax/edit_item/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'X-CSRFToken': csrfToken,
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    body: params
                })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            // Подсвечиваем изменённую строку без изменения скролла
                            row.style.backgroundColor = '#d4edda';
                            setTimeout(() => {
                                row.style.backgroundColor = '';
                            }, 2000);
                            showMessage("success", data.message || "Товар успешно обновлён");
                        } else {
                            showMessage("danger", data.error || "Ошибка при обновлении товара");
                        }
                    })
                    .catch(error => {
                        console.error('Ошибка:', error);
                        showMessage("danger", "Ошибка при выполнении запроса");
                    });
            });
        });

        // ===== AJAX для удаления товара =====
        document.querySelectorAll('button[name="delete_item"]').forEach(button => {
            button.addEventListener('click', function (event) {
                event.preventDefault();
                if (!confirm("Вы действительно хотите удалить этот товар?")) return;
                const itemId = this.value;
                const row = document.getElementById(`item-${itemId}`);
                const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

                const params = new URLSearchParams();
                params.append('delete_item', itemId);

                fetch('/ajax/delete_item/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'X-CSRFToken': csrfToken,
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    body: params
                })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            row.remove();
                            showMessage("success", data.message || "Товар успешно удалён");
                        } else {
                            showMessage("danger", data.error || "Ошибка при удалении товара");
                        }
                    })
                    .catch(error => {
                        console.error('Ошибка:', error);
                        showMessage("danger", "Ошибка при выполнении запроса");
                    });
            });
        });
    }


    // ===== Автоматическая настройка высоты для всех textarea с классом "auto-expand" =====
    document.querySelectorAll(".auto-expand").forEach(textarea => {
        const adjustHeight = () => {
            textarea.style.height = "auto";
            textarea.style.height = textarea.scrollHeight + "px";
        };
        adjustHeight();
        textarea.addEventListener("input", adjustHeight);
    });

    // ===== "Select All" для расчётов (если используется) =====
    const selectAll = document.getElementById("select_all");
    if (selectAll) {
        const checkboxes = document.querySelectorAll("input[name='calc_ids']");
        selectAll.addEventListener("change", () => {
            checkboxes.forEach(cb => cb.checked = selectAll.checked);
        });
    }

    // ===== Перерасчёт итоговых сумм для таблицы расчётов (если присутствует) =====
    if (calculationTable) {
        const totalWithoutMarkupElement = document.getElementById('total-without-markup');
        const totalWithMarkupElement = document.getElementById('total-with-markup');
        const markupInput = document.getElementById('markup');

        const recalculateTotals = () => {
            let totalWithoutMarkup = 0;
            calculationTable.querySelectorAll('tbody tr').forEach(row => {
                const checkbox = row.querySelector('.item-checkbox');
                const priceCell = row.querySelector('.item-price');
                const quantityInput = row.querySelector('.quantity-input');
                const price = parseFloat(priceCell ? priceCell.textContent : "0") || 0;
                const quantity = parseInt(quantityInput ? quantityInput.value : "0") || 0;
                if (checkbox && checkbox.checked) {
                    totalWithoutMarkup += price * quantity;
                }
            });
            const markupValue = parseFloat(markupInput.value) || 0;
            const totalWithMarkup = totalWithoutMarkup + (totalWithoutMarkup * (markupValue / 100));
            totalWithoutMarkupElement.textContent = totalWithoutMarkup.toFixed(2);
            totalWithMarkupElement.textContent = totalWithMarkup.toFixed(2);
        };

        calculationTable.addEventListener('input', recalculateTotals);
        calculationTable.addEventListener('change', recalculateTotals);
        markupInput.addEventListener('input', recalculateTotals);
        recalculateTotals();
    }

    // ===== Подсветка нового товара (если в URL присутствует параметр new_item) =====
    const params = new URLSearchParams(window.location.search);
    const newItemId = params.get('new_item');
    if (newItemId) {
        const newRow = document.getElementById('item-' + newItemId);
        if (newRow) {
            newRow.scrollIntoView({behavior: 'smooth', block: 'center'});
            newRow.style.backgroundColor = '#d4edda';
            setTimeout(() => {
                newRow.style.backgroundColor = '';
            }, 2000);
        }
    }

    // ===== Подсветка изменённого товара (если в URL присутствует параметр changed_item) =====
    const changedItemId = params.get('changed_item');
    if (changedItemId) {
        const changedRow = document.getElementById('item-' + changedItemId);
        if (changedRow) {
            changedRow.style.backgroundColor = '#d4edda';
            setTimeout(() => {
                changedRow.style.backgroundColor = '';
            }, 2000);
        }
    }

    // ===== Функция отображения сообщений =====
    function showMessage(type, text) {
        const messageContainer = document.getElementById("message-container");
        if (!messageContainer) return;
        const alertDiv = document.createElement("div");
        alertDiv.className = `alert alert-${type} alert-dismissible fade show shadow-lg m-2`;
        alertDiv.innerHTML = `
            <strong>${text}</strong>
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        messageContainer.appendChild(alertDiv);
        setTimeout(() => {
            alertDiv.classList.remove("show");
        }, 5000);
        setTimeout(() => {
            alertDiv.remove();
        }, 5500);
    }
});


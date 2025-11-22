function openEditModal(button) {
  const itemId = button.dataset.id;
  const itemName = button.dataset.name;
  const itemPrice = button.dataset.price;

  document.getElementById('editItemId').value = itemId;
  document.getElementById('editItemName').value = itemName;
  document.getElementById('editItemPrice').value = itemPrice;

  const modal = new bootstrap.Modal(document.getElementById('editModal'));
  modal.show();
}

document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('editItemForm');
  const modalElement = document.getElementById('editModal');

  if (!form || !modalElement) {
    return;
  }

  form.addEventListener('submit', (event) => {
    event.preventDefault();

    const itemIdField = document.getElementById('editItemId');
    const nameField = document.getElementById('editItemName');
    const priceField = document.getElementById('editItemPrice');
    const csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');

    if (!itemIdField || !nameField || !priceField || !csrfInput) {
      console.warn('Пропущены поля формы для редактирования товара.');
      return;
    }

    const itemId = itemIdField.value;
    const name = nameField.value;
    const price = priceField.value;

    const body = new URLSearchParams();
    body.append('edit_item', itemId);
    body.append(`name_${itemId}`, name);
    body.append(`price_${itemId}`, price);

    fetch('/ajax/edit_item/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-CSRFToken': csrfInput.value,
        'X-Requested-With': 'XMLHttpRequest',
      },
      body,
    })
      .then((res) => res.json())
      .then((data) => {
        if (data.success) {
          const row = document.getElementById(`item-${itemId}`);
          if (row) {
            row.querySelector('.item-name').textContent = name;
            const priceCell = row.querySelector('td:nth-child(3)');
            if (priceCell) {
              priceCell.textContent = `${parseFloat(price).toFixed(2)} ₽`;
            }
            row.style.backgroundColor = '#d4edda';
            setTimeout(() => {
              row.style.backgroundColor = '';
            }, 2000);
          }
          const modalInstance =
            bootstrap.Modal.getInstance(modalElement) || new bootstrap.Modal(modalElement);
          modalInstance.hide();
        } else {
          alert(data.error || 'Не удалось обновить товар.');
        }
      })
      .catch(() => alert('Ошибка при обращении к серверу.'));
  });
});

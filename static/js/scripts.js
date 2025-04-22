document.addEventListener('DOMContentLoaded', () => {
  const itemTable = document.getElementById('item-table');

  // ===== Редактирование и удаление товара (только на item_list) =====
  if (itemTable) {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    document.querySelectorAll('button[name="edit_item"]').forEach(button => {
      button.addEventListener('click', event => {
        event.preventDefault();
        const itemId = button.value;
        const row = document.getElementById(`item-${itemId}`);
        const nameField = row.querySelector(`textarea[name="name_${itemId}"]`);
        const priceField = row.querySelector(`input[name="price_${itemId}"]`);

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
        .then(res => res.json())
        .then(data => {
          if (data.success) {
            row.style.backgroundColor = '#d4edda';
            setTimeout(() => row.style.backgroundColor = '', 2000);
            showMessage('success', data.message);
          } else {
            showMessage('danger', data.error);
          }
        });
      });
    });

    document.querySelectorAll('button[name="delete_item"]').forEach(button => {
      button.addEventListener('click', event => {
        event.preventDefault();
        if (!confirm("Удалить товар?")) return;
        const itemId = button.value;
        const row = document.getElementById(`item-${itemId}`);
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
        .then(res => res.json())
        .then(data => {
          if (data.success) {
            row.remove();
            showMessage('success', data.message);
          } else {
            showMessage('danger', data.error);
          }
        });
      });
    });
  }

  // ===== Подсветка новых строк =====
  const params = new URLSearchParams(window.location.search);
  const newItemId = params.get('new_item');
  const changedItemId = params.get('changed_item');
  [newItemId, changedItemId].forEach(id => {
    const row = document.getElementById(`item-${id}`);
    if (row) {
      row.scrollIntoView({ behavior: 'smooth', block: 'center' });
      row.style.backgroundColor = '#d4edda';
      setTimeout(() => row.style.backgroundColor = '', 2000);
    }
  });

  // ===== Показывать алерты =====
  function showMessage(type, text) {
    const container = document.getElementById('message-container');
    if (!container) return;
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show shadow-lg m-2`;
    alertDiv.innerHTML = `<strong>${text}</strong><button type="button" class="btn-close" data-bs-dismiss="alert"></button>`;
    container.appendChild(alertDiv);
    setTimeout(() => alertDiv.remove(), 5000);
  }
});

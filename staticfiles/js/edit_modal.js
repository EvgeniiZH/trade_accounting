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
  form.addEventListener('submit', (e) => {
    e.preventDefault();

    const itemId = document.getElementById('editItemId').value;
    const name = document.getElementById('editItemName').value;
    const price = document.getElementById('editItemPrice').value;
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    fetch("/ajax/edit_item/", {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
        "X-CSRFToken": csrfToken,
        "X-Requested-With": "XMLHttpRequest"
      },
      body: new URLSearchParams({
        edit_item: itemId,
        [`name_${itemId}`]: name,
        [`price_${itemId}`]: price
      })
    })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        const row = document.getElementById(`item-${itemId}`);
        if (row) {
          row.querySelector('.item-name').innerHTML = name;
          row.querySelector('td:nth-child(3)').innerHTML = parseFloat(price).toFixed(2) + " ₽";
          row.style.backgroundColor = "#d4edda";
          setTimeout(() => row.style.backgroundColor = "", 2000);
        }
        bootstrap.Modal.getInstance(document.getElementById('editModal')).hide();
      } else {
        alert(data.error || "Ошибка редактирования");
      }
    });
  });
});

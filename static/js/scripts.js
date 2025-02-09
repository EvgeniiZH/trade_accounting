// document.addEventListener("DOMContentLoaded", function () {
//     // Фильтр поиска товаров
//     const searchInput = document.getElementById("search");
//     if (searchInput) {
//         searchInput.addEventListener("input", function () {
//             let filter = searchInput.value.toLowerCase();
//             let rows = document.querySelectorAll("table tbody tr");
//
//             rows.forEach(row => {
//                 let text = row.innerText.toLowerCase();
//                 row.style.display = text.includes(filter) ? "" : "none";
//             });
//         });
//     }
//
//     // Автоисчезновение сообщений
//     setTimeout(() => {
//         let alerts = document.querySelectorAll(".alert");
//         alerts.forEach(alert => {
//             alert.style.display = "none";
//         });
//     }, 3000);
//
//     // Подсветка найденного элемента в поиске
//     document.querySelectorAll("#search-input").forEach((input) => {
//         input.addEventListener("input", function () {
//             let searchTerm = input.value.trim().toLowerCase();
//             let rows = document.querySelectorAll("table tbody tr");
//
//             rows.forEach(row => {
//                 let itemName = row.innerText.toLowerCase();
//                 if (itemName.startsWith(searchTerm)) {
//                     row.scrollIntoView({ behavior: 'smooth', block: 'center' });
//                     row.classList.add("highlight");
//                     setTimeout(() => row.classList.remove("highlight"), 2000);
//                 }
//             });
//         });
//     });
//
//     // Улучшение отображения чекбоксов
//     document.querySelectorAll('input[type="checkbox"]').forEach(checkbox => {
//         checkbox.addEventListener("change", function () {
//             this.closest("tr").classList.toggle("table-warning", this.checked);
//         });
//     });
//
//     // Авторасширение текстовых полей
//     document.querySelectorAll(".auto-expand").forEach((textarea) => {
//         textarea.style.height = textarea.scrollHeight + "px";
//         textarea.addEventListener("input", function () {
//             this.style.height = "auto";
//             this.style.height = this.scrollHeight + "px";
//         });
//     });
// });
//
//
// document.addEventListener("DOMContentLoaded", function () {
//     // Удаление товаров без перезагрузки
//     document.querySelectorAll("[name^='delete_']").forEach(function (checkbox) {
//         checkbox.addEventListener("change", function () {
//             if (this.checked) {
//                 let row = this.closest("tr");
//                 row.classList.add("table-danger");
//             } else {
//                 this.closest("tr").classList.remove("table-danger");
//             }
//         });
//     });
//
//     // Автообновление стоимости при изменении количества
//     document.querySelectorAll("[name^='quantity_']").forEach(function (input) {
//         input.addEventListener("input", function () {
//             let row = this.closest("tr");
//             let price = parseFloat(row.querySelector(".price").textContent);
//             let quantity = parseInt(this.value);
//             let totalCell = row.querySelector(".total-price");
//
//             totalCell.textContent = (price * quantity).toFixed(2);
//         });
//     });
//
//     // Всплывающие сообщения
//     const messages = document.querySelectorAll(".alert");
//     messages.forEach(function (msg) {
//         setTimeout(() => {
//             msg.classList.add("fade");
//             setTimeout(() => msg.remove(), 500);
//         }, 5000);
//     });
// });
//
// function recalculateTotals() {
//     let total = 0;
//     let markup = parseFloat(document.getElementById('markup').value || 0);
//
//     // Перебираем все строки товаров
//     document.querySelectorAll('#itemsTable tr').forEach(function(row) {
//         let price = parseFloat(row.cells[2].innerText);
//         let quantity = parseFloat(row.querySelector('input[type="number"]').value);
//
//         // Рассчитываем стоимость для каждой строки
//         let itemTotal = price * quantity;
//         row.querySelector('.item-total').innerText = itemTotal.toFixed(2);
//
//         total += itemTotal;
//     });
//
//     // Рассчитываем итоговую стоимость с наценкой
//     let totalPriceWithMarkup = total + (total * markup / 100);
//
//     // Отображаем итоговую стоимость
//     document.getElementById('totalPrice').value = totalPriceWithMarkup.toFixed(2);
// }
//
// function removeItemRow(button) {
//     // Удаляем строку товара
//     button.closest('tr').remove();
//     recalculateTotals();  // Пересчитываем итоговую стоимость после удаления
// }

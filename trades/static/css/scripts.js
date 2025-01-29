document.addEventListener('DOMContentLoaded', () => {
    console.log('JavaScript подключён и работает!');

    // Добавьте сюда свои скрипты для обработки взаимодействий
});
document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.querySelector('#search-input');
    const tableBody = document.querySelector('#item-table tbody');

    searchInput.addEventListener('input', () => {
        const searchTerm = searchInput.value.trim().toLowerCase();
        const rows = tableBody.querySelectorAll('tr');
        let found = false;

        rows.forEach(row => {
            const nameInput = row.querySelector("input[name^='name']");
            const itemName = nameInput ? nameInput.value.trim().toLowerCase() : "";

            if (!found && itemName.startsWith(searchTerm)) {
                row.scrollIntoView({behavior: 'smooth', block: 'center'});
                row.style.backgroundColor = '#d4edda'; // Подсветка найденного элемента
                setTimeout(() => row.style.backgroundColor = '', 2000); // Убираем подсветку через 2 секунды
                found = true;
            }
        });

        if (!found) {
            console.log('Товаров не найдено для:', searchTerm);
        }
    });
});

document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".auto-expand").forEach((textarea) => {
        textarea.style.height = textarea.scrollHeight + "px";
        textarea.addEventListener("input", function () {
            this.style.height = "auto"; // Сбрасываем высоту
            this.style.height = this.scrollHeight + "px"; // Устанавливаем новую высоту
        });
    });
});

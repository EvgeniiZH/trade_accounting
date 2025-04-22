document.addEventListener("DOMContentLoaded", function () {
    const messages = window._djangoMessages || [];
    const container = document.getElementById("message-container");

    messages.forEach(msg => {
        const alertDiv = document.createElement("div");
        let alertClass = "alert-info";

        if (msg.tags.includes("success")) alertClass = "alert-success";
        if (msg.tags.includes("error")) alertClass = "alert-danger";
        if (msg.tags.includes("warning")) alertClass = "alert-warning";

        alertDiv.className = `alert ${alertClass} alert-dismissible fade show shadow-lg m-2`;
        alertDiv.innerHTML = `
            <strong>${msg.message}</strong>
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        container.appendChild(alertDiv);

        setTimeout(() => alertDiv.classList.remove("show"), 5000);
        setTimeout(() => alertDiv.remove(), 5500);
    });
});

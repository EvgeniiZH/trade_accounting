document.addEventListener("DOMContentLoaded", () => {
    const messages = window._djangoMessages || [];
    const container = document.getElementById("message-container");
    if (!container || !messages.length) return;

    const TYPE_META = {
        success: { icon: "✅", title: "Готово", css: "message-toast--success", timeout: 4500 },
        error: { icon: "⚠️", title: "Ошибка", css: "message-toast--error", timeout: 6000 },
        warning: { icon: "⚠️", title: "Важно", css: "message-toast--warning", timeout: 5500 },
        info: { icon: "ℹ️", title: "Инфо", css: "message-toast--info", timeout: 4000 },
    };

    function pickMeta(tags = "") {
        if (!tags) return TYPE_META.info;
        for (const key of Object.keys(TYPE_META)) {
            if (tags.includes(key)) return TYPE_META[key];
        }
        return TYPE_META.info;
    }

    function buildToast(msg) {
        const meta = pickMeta(msg.tags || "");

        const toast = document.createElement("div");
        toast.className = `message-toast ${meta.css}`;
        toast.setAttribute("role", "status");

        toast.innerHTML = `
            <div class="message-toast__icon">${meta.icon}</div>
            <div class="message-toast__body">
                <div class="message-toast__title">${meta.title}</div>
                <p class="message-toast__text">${msg.message}</p>
            </div>
            <button class="message-toast__close" type="button" aria-label="Закрыть" data-toast-close>&times;</button>
            <div class="message-toast__progress">
                <span class="message-toast__progress-bar"></span>
            </div>
        `;

        const progressBar = toast.querySelector(".message-toast__progress-bar");
        requestAnimationFrame(() => {
            toast.classList.add("enter");
            progressBar.style.transition = `transform ${meta.timeout}ms linear`;
            progressBar.style.transform = "scaleX(0)";
        });

        const hideToast = () => {
            toast.classList.add("exit");
            toast.classList.remove("enter");
            setTimeout(() => toast.remove(), 350);
        };

        const timerId = setTimeout(() => hideToast(), meta.timeout);

        toast.querySelector("[data-toast-close]").addEventListener("click", () => {
            clearTimeout(timerId);
            hideToast();
        });

        toast.addEventListener("mouseenter", () => clearTimeout(timerId));

        return toast;
    }

    messages.forEach(msg => {
        const toast = buildToast(msg);
        container.appendChild(toast);
    });
});

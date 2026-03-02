// HTMX CSRF token injection for all requests
document.body.addEventListener("htmx:configRequest", function (event) {
    const csrfMeta = document.querySelector('input[name="csrf_token"]');
    if (csrfMeta) {
        event.detail.headers["X-CSRFToken"] = csrfMeta.value;
    }
});

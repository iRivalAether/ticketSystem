/**
 * frontend.js - Microinteractions y animaciones - inicial
 * - Reveal on scroll
 * - Inicializa tooltips de Bootstrap
 * - Pequeñas mejoras en botones e íconos
 */

document.addEventListener('DOMContentLoaded', function() {
    // Inicializar tooltips (Bootstrap)
    if (window.bootstrap && bootstrap.Tooltip) {
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (el) { return new bootstrap.Tooltip(el); });
    }

    // Reveal on scroll
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('is-visible');
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.12 });

    document.querySelectorAll('.fade-up').forEach(el => observer.observe(el));

    // Small hover animation for icons with class .icon-animate
    document.querySelectorAll('.icon-animate').forEach(icon => {
        icon.addEventListener('mouseenter', () => icon.style.transform = 'translateY(-2px) rotate(-6deg)');
        icon.addEventListener('mouseleave', () => icon.style.transform = 'none');
    });

    // Enhance form controls: add focus class
    document.querySelectorAll('.form-control').forEach(inp => {
        inp.addEventListener('focus', () => inp.classList.add('focus-ring'));
        inp.addEventListener('blur', () => inp.classList.remove('focus-ring'));
    });
});

// Smooth scroll helper
function smoothScrollTo(selector) {
    const el = document.querySelector(selector);
    if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

// Exponer helper globalmente (evita usar export que rompe en scripts normales)
window.smoothScrollTo = smoothScrollTo;

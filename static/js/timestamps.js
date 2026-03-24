/**
 * timestamps.js - Recalcular timestamps dinámicamente sin hacer fetch
 * 
 * Convierte "hace 5 segundos" a "hace 6 segundos", "hace 7 segundos", etc.
 * automáticamente cada 1 segundo, sin necesidad de recargar la página.
 */

/**
 * Obtener diferencia de tiempo en formato legible
 * @param {Date|string} date - Fecha ISO o Date object
 * @returns {string} Formato: "hace 5 segundos", "hace 2 minutos", etc.
 */
function getTimeSinceHuman(date) {
    if (typeof date === 'string') {
        try {
            date = new Date(date);
        } catch (e) {
            return '';
        }
    }

    const now = new Date();
    const secondsElapsed = Math.floor((now - date) / 1000);

    if (secondsElapsed < 60) {
        return 'hace ' + secondsElapsed + ' segundo' + (secondsElapsed !== 1 ? 's' : '');
    }

    const minutesElapsed = Math.floor(secondsElapsed / 60);
    if (minutesElapsed < 60) {
        return 'hace ' + minutesElapsed + ' minuto' + (minutesElapsed !== 1 ? 's' : '');
    }

    const hoursElapsed = Math.floor(minutesElapsed / 60);
    if (hoursElapsed < 24) {
        return 'hace ' + hoursElapsed + ' hora' + (hoursElapsed !== 1 ? 's' : '');
    }

    const daysElapsed = Math.floor(hoursElapsed / 24);
    if (daysElapsed < 7) {
        return 'hace ' + daysElapsed + ' día' + (daysElapsed !== 1 ? 's' : '');
    }

    const weeksElapsed = Math.floor(daysElapsed / 7);
    if (weeksElapsed < 4) {
        return 'hace ' + weeksElapsed + ' semana' + (weeksElapsed !== 1 ? 's' : '');
    }

    const monthsElapsed = Math.floor(daysElapsed / 30);
    if (monthsElapsed < 12) {
        return 'hace ' + monthsElapsed + ' mes' + (monthsElapsed !== 1 ? 'es' : '');
    }

    const yearsElapsed = Math.floor(monthsElapsed / 12);
    return 'hace ' + yearsElapsed + ' año' + (yearsElapsed !== 1 ? 's' : '');
}

/**
 * Actualizar todos los elementos que tienen data-timestamp
 * Se ejecuta cada 1 segundo automáticamente
 */
function updateTimestamps() {
    // Buscar todos los elementos con atributo data-timestamp
    const elements = document.querySelectorAll('[data-timestamp]');

    elements.forEach(el => {
        const isoDate = el.getAttribute('data-timestamp');
        if (!isoDate) return;

        const newText = getTimeSinceHuman(isoDate);
        if (newText && el.textContent !== newText) {
            el.textContent = newText;
        }
    });
}

/**
 * Inicializar actualización automática de timestamps
 * Se ejecuta cada 1 segundo
 */
function startTimestampUpdates(intervalMs = 1000) {
    // Actualizar inmediatamente al cargar
    updateTimestamps();

    // Luego actualizar cada X ms (default 1 segundo)
    setInterval(updateTimestamps, intervalMs);
}

/**
 * Al cargar el DOM, iniciar las actualizaciones
 */
document.addEventListener('DOMContentLoaded', function() {
    startTimestampUpdates(1000); // Actualizar cada 1 segundo
});

// Expo para uso manual
window.TimestampUpdater = {
    update: updateTimestamps,
    start: startTimestampUpdates,
    getTimeSince: getTimeSinceHuman
};

/**
 * date-inputs.js - Validación visual para inputs de fecha y fecha-hora
 */

function normalizeDateInputValue(value, kind) {
    if (!value) {
        return '';
    }

    const date = new Date(value);
    if (Number.isNaN(date.getTime())) {
        return '';
    }

    const pad = (number) => String(number).padStart(2, '0');
    const year = date.getFullYear();
    const month = pad(date.getMonth() + 1);
    const day = pad(date.getDate());

    if (kind === 'datetime-local') {
        const hours = pad(date.getHours());
        const minutes = pad(date.getMinutes());
        return `${year}-${month}-${day}T${hours}:${minutes}`;
    }

    return `${year}-${month}-${day}`;
}

function bindDateInputValidation(input) {
    const kind = input.dataset.dateInput || input.type;

    const validate = () => {
        const normalized = normalizeDateInputValue(input.value, kind);
        if (!input.value) {
            input.setCustomValidity('');
            return;
        }

        if (!normalized) {
            input.setCustomValidity('Formato de fecha inválido');
            input.classList.add('input-invalid');
            return;
        }

        input.setCustomValidity('');
        input.classList.remove('input-invalid');
    };

    input.addEventListener('blur', validate);
    input.addEventListener('change', validate);
    input.addEventListener('input', validate);

    validate();
}

document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('input[data-date-input], input[type="date"], input[type="datetime-local"]').forEach(bindDateInputValidation);
});
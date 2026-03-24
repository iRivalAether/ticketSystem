/**
 * realtime-updates.js - Polling automático y actualización de datos en tiempo real
 * 
 * Función principal: setupRealtimePolling()
 * Hace fetch a APIs cada X segundos y actualiza gráficos + KPIs
 */

// Configuración global de polling
const realtimeConfig = {
    interval: 2000, // 2 segundos (puede ser 1000 para más frecuente)
    dashboardEnabled: true,
    reportesEnabled: true,
    lastUpdate: null
};

/**
 * Configurar polling en tiempo real
 * @param {number} intervalMs - Intervalo en milisegundos (default 2000ms = 2 sec)
 */
function setupRealtimePolling(intervalMs = 2000) {
    realtimeConfig.interval = intervalMs;

    // Polling del dashboard (KPIs principales)
    if (document.getElementById('mis-tickets-abiertos')) {
        setupDashboardPolling();
    }

    // Polling de reportes (gráficos)
    if (document.getElementById('chart-sla-gauge')) {
        setupReportesPolling();
    }
}

/**
 * Setup polling para dashboard principal
 * Actualiza KPIs: mis_tickets_abiertos, tickets_en_atencion, cumplimiento_sla, etc.
 */
function setupDashboardPolling() {
    setInterval(function() {
        fetch('/api/dashboard/stats/')
            .then(response => response.json())
            .then(data => {
                updateDashboardMetrics(data);
                updateLastUpdateTime();
            })
            .catch(error => console.error('Error polling dashboard:', error));
    }, realtimeConfig.interval);
}

/**
 * Actualizar métricas del dashboard
 * @param {object} data - Datos del API
 */
function updateDashboardMetrics(data) {
    // Actualizar tiles de KPIs
    if (data.mis_tickets_abiertos !== undefined) {
        updateElementText('mis-tickets-abiertos', data.mis_tickets_abiertos);
    }
    if (data.tickets_en_atencion !== undefined) {
        updateElementText('tickets-en-atencion', data.tickets_en_atencion);
    }
    if (data.cumplimiento_sla !== undefined) {
        updateElementText('cumplimiento-sla', data.cumplimiento_sla.toFixed(1) + '%');
    }
    if (data.promedio_atencion !== undefined) {
        updateElementText('promedio-atencion', Math.round(data.promedio_atencion) + ' min');
    }
    if (data.promedio_resolucion !== undefined) {
        updateElementText('promedio-resolucion', (data.promedio_resolucion / 60).toFixed(1) + ' h');
    }

    // Actualizar FIFO próximo ticket (si existe)
    if (data.proximo_ticket) {
        const nextTicketEl = document.getElementById('proximo-ticket');
        if (nextTicketEl) {
            nextTicketEl.innerHTML = `
                <div class="ticket-card">
                    <strong>#${data.proximo_ticket.numero}</strong>
                    <p>${data.proximo_ticket.asunto}</p>
                    <small>${data.proximo_ticket.estado}</small>
                </div>
            `;
        }
    }
}

/**
 * Setup polling para reportes (gráficos avanzados)
 * Actualiza: SLA gauge, Tendencia línea, Distribuciones pie, Tiempos bar, Heatmap
 */
function setupReportesPolling() {
    fetchReportesData();

    setInterval(function() {
        fetchReportesData();
    }, realtimeConfig.interval);
}

function fetchReportesData() {
    const periodo = getFilterValue('periodo', '30d');
    const area = getFilterValue('area', '');
    const jornada = getFilterValue('jornada', '');
    const prioridad = getFilterValue('prioridad', '');

    const params = new URLSearchParams({
        periodo: periodo,
        ...(area && { area: area }),
        ...(jornada && { jornada: jornada }),
        ...(prioridad && { prioridad: prioridad })
    });

    fetch('/api/reportes/datos-filtrados/?' + params.toString())
        .then(response => response.json())
        .then(data => {
            updateReportesCharts(data);
            updateLastUpdateTime();
        })
        .catch(error => console.error('Error polling reportes:', error));
}

/**
 * Actualizar todos los gráficos en reportes
 * @param {object} data - Datos del API con estadísticas, desglose, series_temporal
 */
function updateReportesCharts(data) {
    // 1. SLA Gauge
    if (data.estadisticas && data.estadisticas.sla) {
        const cumplimiento = data.estadisticas.sla.cumplimiento_porcentaje || 0;
        updateSLAGauge('chart-sla-gauge', cumplimiento);

        // Actualizar tiles de conteos
        updateElementText('sla-verde-count', data.estadisticas.sla.sla_verde || 0);
        updateElementText('sla-amarillo-count', data.estadisticas.sla.sla_amarillo || 0);
        updateElementText('sla-rojo-count', data.estadisticas.sla.sla_rojo || 0);
    }

    // 2. Tendencia Línea (serie temporal por hora)
    if (data.series_temporal && data.series_temporal.length > 0) {
        const horas = data.series_temporal.map(s => new Date(s.hora).getHours() + ':00');
        const counts = data.series_temporal.map(s => s.count);
        updateTendenciaLinea('chart-tendencia-linea', horas, counts);
    }

    // 3. Distribución Pie por Área
    if (data.desglose && data.desglose.por_area) {
        const labels = Object.keys(data.desglose.por_area);
        const counts = labels.map(area => data.desglose.por_area[area].total);
        updateDistribucionPie('chart-distribucion-area', labels, counts);
    }

    // 4. Distribución Pie por Jornada
    if (data.desglose && data.desglose.por_jornada) {
        const labels = Object.keys(data.desglose.por_jornada);
        const counts = labels.map(jornada => data.desglose.por_jornada[jornada].total);
        updateDistribucionPie('chart-distribucion-jornada', labels, counts);
    }

    // 5. Tiempos Bar (por área)
    if (data.desglose && data.desglose.por_area && data.estadisticas.tiempos) {
        const areas = Object.keys(data.desglose.por_area);
        // Simulado: usar promedios globales (ideal: desglosar por área en API)
        const atencion = areas.map(() => data.estadisticas.tiempos.promedio_primera_atencion_minutos || 0);
        const resolucion = areas.map(() => data.estadisticas.tiempos.promedio_resolucion_horas || 0);
        updateTiemposBar('chart-tiempos-bar', areas, atencion, resolucion);
    }

    // 6. Heatmap Jornada (opcional, si se implementa en API)
    if (data.heatmap_jornada) {
        updateHeatmapJornada('chart-heatmap-jornada', data.heatmap_jornada);
    }
}

/**
 * Obtener valor de filtro desde formulario o localStorage
 * @param {string} fieldId - ID del campo (ej: "periodo", "area")
 * @param {string} defaultValue - Valor por defecto
 * @returns {string} Valor del filtro
 */
function getFilterValue(fieldId, defaultValue = '') {
    const el = document.getElementById('filter-' + fieldId) || document.getElementById(fieldId);
    if (!el) {
        // Intentar recuperar de localStorage
        return localStorage.getItem('filter_' + fieldId) || defaultValue;
    }
    const value = el.value || defaultValue;
    localStorage.setItem('filter_' + fieldId, value);
    return value;
}

/**
 * Actualizar el texto de un elemento por ID
 * @param {string} elementId - ID del elemento
 * @param {string|number} newValue - Nuevo valor
 */
function updateElementText(elementId, newValue) {
    const el = document.getElementById(elementId);
    if (el) {
        el.textContent = newValue;
    }
}

/**
 * Actualizar timestamp "última actualización: hace XX segundos"
 */
function updateLastUpdateTime() {
    const el = document.getElementById('last-update-time');
    if (el) {
        const now = new Date();
        const timeStr = now.toLocaleTimeString('es-ES');
        el.textContent = 'Actualizado: ' + timeStr;
        el.title = now.toString();
    }
}

/**
 * Setup listeners para cambios de filtros
 * Cuando el usuario cambia un filtro, resetear polling para obtener nuevos datos inmediatamente
 */
function setupFilterListeners() {
    ['periodo', 'area', 'jornada', 'prioridad'].forEach(filtro => {
        const el = document.getElementById('filter-' + filtro) || document.getElementById(filtro);
        if (el) {
            el.addEventListener('change', function() {
                // Guardar en localStorage
                localStorage.setItem('filter_' + filtro, this.value);
                fetchReportesData();
            });
        }
    });
}

/**
 * Inicializar todo al cargar la página
 */
document.addEventListener('DOMContentLoaded', function() {
    setupRealtimePolling(2000); // Polling cada 2 segundos
    setupFilterListeners();
    updateLastUpdateTime();
});

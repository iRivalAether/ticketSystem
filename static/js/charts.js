/**
 * charts.js - Funciones para crear y actualizar gráficos con Chart.js
 * 
 * 5 tipos de gráficos:
 * - SLA Gauge (semicírculo de cumplimiento)
 * - Tendencia Línea (tickets por hora)
 * - Distribución Pie (por área/jornada/prioridad)
 * - Tiempos Bar (promedios por categoría)
 * - Heatmap (carga por jornada x hora)
 */

// Objeto global para almacenar referencias a gráficos
const chartsRegistry = {};

/**
 * Inicializar SLA Gauge (semicírculo con porcentaje)
 * @param {string} containerId - ID del contenedor
 * @param {number} porcentaje - % de cumplimiento (0-100)
 * @param {string} titulo - Título del gráfico
 */
function initSLAGauge(containerId, porcentaje, titulo = 'Cumplimiento SLA') {
    const ctx = document.getElementById(containerId);
    if (!ctx) return;

    if (chartsRegistry[containerId]) {
        chartsRegistry[containerId].destroy();
    }

    const chart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Dentro de SLA', 'Fuera de SLA'],
            datasets: [{
                data: [porcentaje, 100 - porcentaje],
                backgroundColor: [
                    '#27ae60', // Verde
                    '#ecf0f1'  // Gris claro
                ],
                borderColor: '#fff',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'bottom',
                    labels: {
                        font: { size: 12 },
                        padding: 15
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.label + ': ' + context.parsed.toFixed(1) + '%';
                        }
                    }
                }
            }
        }
    });

    chartsRegistry[containerId] = chart;
    return chart;
}

/**
 * Actualizar SLA Gauge
 * @param {string} containerId - ID del contenedor
 * @param {number} porcentaje - Nuevo porcentaje
 */
function updateSLAGauge(containerId, porcentaje) {
    if (!chartsRegistry[containerId]) {
        initSLAGauge(containerId, porcentaje);
        return;
    }
    const chart = chartsRegistry[containerId];
    chart.data.datasets[0].data = [porcentaje, 100 - porcentaje];
    chart.update('none'); // 'none' para actualización sin animación
}

/**
 * Inicializar Tendencia Línea
 * @param {string} containerId - ID del contenedor
 * @param {array} horas - Array de horas ["00:00", "01:00", ...]
 * @param {array} datos - Array de conteos [5, 3, 8, ...]
 */
function initTendenciaLinea(containerId, horas, datos) {
    const ctx = document.getElementById(containerId);
    if (!ctx) return;

    if (chartsRegistry[containerId]) {
        chartsRegistry[containerId].destroy();
    }

    const chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: horas,
            datasets: [{
                label: 'Tickets Creados',
                data: datos,
                borderColor: '#D4AF37', // Dorado
                backgroundColor: 'rgba(212, 175, 55, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4,
                pointRadius: 4,
                pointBackgroundColor: '#D4AF37',
                pointBorderColor: '#fff',
                pointBorderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            }
        }
    });

    chartsRegistry[containerId] = chart;
    return chart;
}

/**
 * Actualizar Tendencia Línea
 * @param {string} containerId - ID del contenedor
 * @param {array} horas - Array de horas
 * @param {array} datos - Array de conteos
 */
function updateTendenciaLinea(containerId, horas, datos) {
    if (!chartsRegistry[containerId]) {
        initTendenciaLinea(containerId, horas, datos);
        return;
    }
    const chart = chartsRegistry[containerId];
    chart.data.labels = horas;
    chart.data.datasets[0].data = datos;
    chart.update('none');
}

/**
 * Inicializar Distribución Pie
 * @param {string} containerId - ID del contenedor
 * @param {array} labels - Etiquetas ["Soporte", "Infraestructura", ...]
 * @param {array} datos - Conteos [25, 18, ...]
 * @param {string} titulo - Título del gráfico
 */
function initDistribucionPie(containerId, labels, datos, titulo = 'Distribución por Área') {
    const ctx = document.getElementById(containerId);
    if (!ctx) return;

    if (chartsRegistry[containerId]) {
        chartsRegistry[containerId].destroy();
    }

    const colores = [
        '#27ae60', // Verde
        '#e74c3c', // Rojo
        '#f39c12', // Naranja
        '#3498db', // Azul
        '#9b59b6', // Púrpura
        '#1abc9c'  // Turquesa
    ];

    const chart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: datos,
                backgroundColor: colores.slice(0, labels.length),
                borderColor: '#fff',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'bottom',
                    labels: {
                        font: { size: 11 },
                        padding: 15
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((context.parsed / total) * 100).toFixed(1);
                            return context.label + ': ' + context.parsed + ' (' + percentage + '%)';
                        }
                    }
                }
            }
        }
    });

    chartsRegistry[containerId] = chart;
    return chart;
}

/**
 * Actualizar Distribución Pie
 * @param {string} containerId - ID del contenedor
 * @param {array} labels - Etiquetas
 * @param {array} datos - Conteos
 */
function updateDistribucionPie(containerId, labels, datos) {
    if (!chartsRegistry[containerId]) {
        initDistribucionPie(containerId, labels, datos);
        return;
    }
    const chart = chartsRegistry[containerId];
    chart.data.labels = labels;
    chart.data.datasets[0].data = datos;
    chart.update('none');
}

/**
 * Inicializar Tiempos Bar (Promedio de atención/resolución por área)
 * @param {string} containerId - ID del contenedor
 * @param {array} labels - Categorías ["Soporte", "Infraestructura", ...]
 * @param {array} atencion - Tiempos promedio de atención (minutos)
 * @param {array} resolucion - Tiempos promedio de resolución (horas)
 */
function initTiemposBar(containerId, labels, atencion, resolucion) {
    const ctx = document.getElementById(containerId);
    if (!ctx) return;

    if (chartsRegistry[containerId]) {
        chartsRegistry[containerId].destroy();
    }

    const chart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Promedio Atención (min)',
                    data: atencion,
                    backgroundColor: '#3498db', // Azul
                    borderColor: '#2980b9',
                    borderWidth: 1
                },
                {
                    label: 'Promedio Resolución (h)',
                    data: resolucion,
                    backgroundColor: '#f39c12', // Naranja
                    borderColor: '#d68910',
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: 'y',
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                }
            },
            scales: {
                x: {
                    beginAtZero: true
                }
            }
        }
    });

    chartsRegistry[containerId] = chart;
    return chart;
}

/**
 * Actualizar Tiempos Bar
 * @param {string} containerId - ID del contenedor
 * @param {array} labels - Categorías
 * @param {array} atencion - Tiempos de atención
 * @param {array} resolucion - Tiempos de resolución
 */
function updateTiemposBar(containerId, labels, atencion, resolucion) {
    if (!chartsRegistry[containerId]) {
        initTiemposBar(containerId, labels, atencion, resolucion);
        return;
    }
    const chart = chartsRegistry[containerId];
    chart.data.labels = labels;
    chart.data.datasets[0].data = atencion;
    chart.data.datasets[1].data = resolucion;
    chart.update('none');
}

/**
 * Inicializar Heatmap de Carga (Tickets por jornada x hora)
 * Usa tabla HTML con colores de fondo según intensidad
 * @param {string} containerId - ID del contenedor
 * @param {object} datos - { jornada: [count, count, ...], ... }
 */
function initHeatmapJornada(containerId, datos) {
    const container = document.getElementById(containerId);
    if (!container) return;

    // Encontrar máximo para escala de colores
    let max = 0;
    Object.values(datos).forEach(jornada => {
        const m = Math.max(...jornada);
        if (m > max) max = m;
    });

    // Crear tabla HTML
    let html = '<table class="heatmap-table">';
    html += '<thead><tr><th>Jornada</th>';
    for (let i = 0; i < 24; i++) {
        html += '<th>' + String(i).padStart(2, '0') + 'h</th>';
    }
    html += '</tr></thead><tbody>';

    Object.entries(datos).forEach(([jornada, counts]) => {
        html += '<tr><td class="jornada-label">' + jornada + '</td>';
        counts.forEach(count => {
            const intensity = max > 0 ? count / max : 0;
            const bgColor = getHeatmapColor(intensity);
            html += '<td title="' + count + ' tickets" style="background-color: ' + bgColor + '; text-align: center; color: #fff; font-weight: bold;">' + (count > 0 ? count : '') + '</td>';
        });
        html += '</tr>';
    });

    html += '</tbody></table>';
    container.innerHTML = html;
}

/**
 * Obtener color para heatmap según intensidad (0-1)
 * @param {number} intensity - Valor de 0 a 1
 * @returns {string} Color en formato RGB
 */
function getHeatmapColor(intensity) {
    if (intensity < 0.33) {
        // Verde
        const g = 200 + Math.floor(intensity * 55);
        return 'rgb(39, 174, 96)';
    } else if (intensity < 0.66) {
        // Amarillo
        return 'rgb(241, 196, 15)';
    } else {
        // Rojo
        return 'rgb(231, 76, 60)';
    }
}

/**
 * Actualizar Heatmap
 * @param {string} containerId - ID del contenedor
 * @param {object} datos - Nuevos datos
 */
function updateHeatmapJornada(containerId, datos) {
    initHeatmapJornada(containerId, datos); // Re-renderizar tabla
}

/**
 * Destruir todos los gráficos (util para limpiar)
 */
function destroyAllCharts() {
    Object.values(chartsRegistry).forEach(chart => {
        if (chart && typeof chart.destroy === 'function') {
            chart.destroy();
        }
    });
    chartsRegistry = {};
}

// backend/static/js/dashboard.js
document.addEventListener('DOMContentLoaded', () => {
    // --- 1. Inisialisasi Komponen ---
    const socket = io();
    const notificationToast = new bootstrap.Toast(document.getElementById('notificationToast'));
    const toastMessageElement = document.getElementById('toastMessage');

    // Konfigurasi untuk grafik
    const chartOptions = {
        scales: {
            y: {
                beginAtZero: false
            }
        },
        animation: {
            duration: 0 // Nonaktifkan animasi untuk update real-time yang lebih halus
        },
        plugins: {
            legend: {
                display: false
            }
        }
    };

    // Buat instance grafik suhu
    const tempCtx = document.getElementById('temperatureChart').getContext('2d');
    const temperatureChart = new Chart(tempCtx, {
        type: 'line',
        data: {
            labels: [], // Label waktu akan diisi nanti
            datasets: [{
                label: 'Suhu (°C)',
                data: [],
                borderColor: 'rgba(255, 99, 132, 1)',
                backgroundColor: 'rgba(255, 99, 132, 0.2)',
                tension: 0.1
            }]
        },
        options: chartOptions
    });

    // Buat instance grafik tekanan
    const pressureCtx = document.getElementById('pressureChart').getContext('2d');
    const pressureChart = new Chart(pressureCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Tekanan (Bar)',
                data: [],
                borderColor: 'rgba(54, 162, 235, 1)',
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                tension: 0.1
            }]
        },
        options: chartOptions
    });

    // Fungsi untuk memperbarui grafik
    function updateCharts(data) {
        const now = new Date();
        const timeLabel = now.toLocaleTimeString();

        // Tentukan jumlah maksimum data yang ditampilkan
        const maxDataPoints = 20;

        // Update Grafik Suhu
        if (temperatureChart.data.labels.length >= maxDataPoints) {
            temperatureChart.data.labels.shift();
            temperatureChart.data.datasets[0].data.shift();
        }
        temperatureChart.data.labels.push(timeLabel);
        temperatureChart.data.datasets[0].data.push(data.temperature);
        temperatureChart.update();

        // Update Grafik Tekanan
        if (pressureChart.data.labels.length >= maxDataPoints) {
            pressureChart.data.labels.shift();
            pressureChart.data.datasets[0].data.shift();
        }
        pressureChart.data.labels.push(timeLabel);
        pressureChart.data.datasets[0].data.push(data.pressure);
        pressureChart.update();
    }

    // --- 2. Event Listener dari Server ---
    socket.on('opc_data_update', (data) => {
        console.log('Menerima data dari server:', data);

        // Update status pompa
        const pumpStatusElement = document.getElementById('pump_status');
        const pumpStatusIcon = document.getElementById('pumpStatusIcon');
        pumpStatusElement.innerText = data.pump_status;

        if (data.pump_status === 'ON') {
            pumpStatusIcon.style.color = 'green';
        } else {
            pumpStatusIcon.style.color = 'red';
        }

        // Update grafik
        updateCharts(data);
    });

    socket.on('command_response', (data) => {
        console.log('Respon perintah dari server:', data.status);
        // Tampilkan notifikasi toast
        toastMessageElement.innerText = data.status;
        notificationToast.show();
    });

    // --- 3. Event Listener dari User (Tombol) ---
    document.getElementById('startPump').addEventListener('click', () => {
        socket.emit('control_command', { command: 'START_PUMP' });
    });

    document.getElementById('stopPump').addEventListener('click', () => {
        socket.emit('control_command', { command: 'STOP_PUMP' });
    });
});
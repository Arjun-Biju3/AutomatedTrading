
var ctx = document.getElementById('stockChart').getContext('2d');
var stockChart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul'],
        datasets: [{
            label: '{{ stock.name }} Stock Price',
            data: [120, 130, 125, 140, 135, 150, 145],
            backgroundColor: 'rgba(26, 115, 232, 0.1)',
            borderColor: '#1a73e8',
            borderWidth: 2,
            fill: true,
            tension: 0.4
        }]
    },
    options: {
        responsive: true,
        plugins: {
            legend: { display: false }
        }
    }
});
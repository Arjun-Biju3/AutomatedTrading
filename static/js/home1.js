
// Set up the chart
var ctx = document.getElementById('stockChart').getContext('2d');
var stockChart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Mon', 'Tue'],
        datasets: [{
            label: 'AAPL',
            data: [142, 145, 146, 144, 147, 145, 148],
            borderColor: '#1a73e8',
            backgroundColor: 'rgba(26, 115, 232, 0.1)',
            borderWidth: 3,
            fill: true,
            pointBackgroundColor: 'white',
            pointBorderColor: '#1a73e8',
            pointBorderWidth: 2,
            pointRadius: 4,
            pointHoverRadius: 6,
            tension: 0.4
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            y: {
                beginAtZero: false,
                grid: {
                    color: 'rgba(0, 0, 0, 0.05)'
                }
            },
            x: {
                grid: {
                    display: false
                }
            }
        },
        plugins: {
            legend: {
                display: false
            },
            tooltip: {
                backgroundColor: 'rgba(0, 0, 0, 0.7)',
                padding: 10,
                caretSize: 6,
                displayColors: false,
                callbacks: {
                    label: function(context) {
                        return '$' + context.raw;
                    }
                }
            }
        },
        interaction: {
            mode: 'index',
            intersect: false,
        }
    }
});

// Simple script to calculate total value
document.getElementById('quantity').addEventListener('input', updateTotalValue);
document.getElementById('stock').addEventListener('change', updateMarketPrice);

function updateMarketPrice() {
    const stockPrices = {
        'AAPL': 145.30,
        'AMZN': 3210.20,
        'GOOGL': 2750.50,
        'TSLA': 843.03
    };
    
    const selectedStock = document.getElementById('stock').value;
    const price = stockPrices[selectedStock];
    document.getElementById('price').value = '$' + price.toFixed(2);
    updateTotalValue();
}

function updateTotalValue() {
    const quantity = document.getElementById('quantity').value;
    const price = parseFloat(document.getElementById('price').value.slice(1));
    const totalValue = (quantity * price).toFixed(2);
    document.getElementById('totalValue').value = '$' + totalValue;
}

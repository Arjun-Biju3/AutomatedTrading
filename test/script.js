const apiKey = "BEIOJDP5J3PG7DO3";
let stockChart;

async function getStockData() {
    const symbol = document.getElementById("stockSymbol").value;
    const marketIndex = document.getElementById("marketIndex").value;
    const timeFrame = parseInt(document.getElementById("timeFrame").value);
    const chartType = document.getElementById("chartType").value;

    if (!symbol && !marketIndex) {
        alert("Please select a stock or market index.");
        return;
    }

    const selectedSymbol = symbol || marketIndex;
    const url = `https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=${selectedSymbol}&apikey=${apiKey}`;

    try {
        const response = await fetch(url);
        const data = await response.json();

        if (!data["Time Series (Daily)"]) {
            document.getElementById("stockInfo").innerHTML = `<p style="color: red;">Invalid Stock Symbol or Market Index</p>`;
            return;
        }

        const timeSeries = data["Time Series (Daily)"];
        const dates = Object.keys(timeSeries).slice(0, timeFrame).reverse();

        const prices = dates.map(date => parseFloat(timeSeries[date]["4. close"]));
        const openPrices = dates.map(date => parseFloat(timeSeries[date]["1. open"]));
        const highPrices = dates.map(date => parseFloat(timeSeries[date]["2. high"]));
        const lowPrices = dates.map(date => parseFloat(timeSeries[date]["3. low"]));

        displayStockInfo(selectedSymbol, timeSeries[dates[dates.length - 1]]);
        updateChart(dates, prices, openPrices, highPrices, lowPrices, selectedSymbol, chartType);
    } catch (error) {
        console.error("Error fetching stock data:", error);
        document.getElementById("stockInfo").innerHTML = `<p style="color: red;">Error fetching stock data.</p>`;
    }
}

function displayStockInfo(symbol, latestData) {
    document.getElementById("stockInfo").innerHTML = `
        <h3>${symbol} Stock Data</h3>
        <p>📉 Price: <b>$${latestData["4. close"]}</b></p>
        <p>📊 Open: <b>$${latestData["1. open"]}</b></p>
        <p>🔼 High: <b>$${latestData["2. high"]}</b></p>
        <p>🔽 Low: <b>$${latestData["3. low"]}</b></p>
        <p>📈 Volume: <b>${latestData["5. volume"]}</b></p>
    `;
}

function updateChart(labels, closePrices, openPrices, highPrices, lowPrices, symbol, chartType) {
    const ctx = document.getElementById("stockChart").getContext("2d");

    if (stockChart) {
        stockChart.destroy();
    }

    let datasets = [{
        label: `${symbol} Stock Price`,
        data: closePrices,
        borderColor: "#007bff",
        backgroundColor: chartType === "line" ? "rgba(0, 123, 255, 0.6)" : "#007bff",
        borderWidth: 2,
        pointRadius: 5,
        pointBackgroundColor: "#0056b3",
        pointHoverRadius: 7,
        tension: 0.4,
        fill: chartType === "line"
    }];

    if (chartType === "candlestick") {
        datasets = [{
            label: `${symbol} Candlestick`,
            data: labels.map((date, index) => ({
                x: date,
                y: [openPrices[index], highPrices[index], lowPrices[index], closePrices[index]]
            })),
            borderColor: "#28a745",
            backgroundColor: "#28a745",
            borderWidth: 1,
        }];
    }

    stockChart = new Chart(ctx, {
        type: chartType === "candlestick" ? "bar" : chartType,
        data: { labels: labels, datasets: datasets },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: { title: { display: true, text: "Date", color: "#555", font: { size: 14, weight: "bold" } }, grid: { display: false } },
                y: { title: { display: true, text: "Stock Price (USD)", color: "#555", font: { size: 14, weight: "bold" } }, grid: { color: "rgba(200, 200, 200, 0.2)" } }
            },
            plugins: {
                legend: { display: true, labels: { color: "#333", font: { size: 14, weight: "bold" } } },
                tooltip: { backgroundColor: "#007bff", titleFont: { size: 14, weight: "bold" }, bodyFont: { size: 12 }, padding: 10, cornerRadius: 5 }
            }
        }
    });
}

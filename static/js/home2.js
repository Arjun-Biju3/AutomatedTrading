document.addEventListener("DOMContentLoaded", function () {
    const stockSelect = document.getElementById("stock");
    const quantityInput = document.getElementById("quantity");
    const priceInput = document.getElementById("price");
    const totalValueInput = document.getElementById("totalValue");

    function updatePriceAndTotal() {
        const selectedStock = stockSelect.options[stockSelect.selectedIndex];
        const price = parseFloat(selectedStock.getAttribute("data-price"));
        const quantity = parseInt(quantityInput.value);
        
        if (!isNaN(price) && !isNaN(quantity)) {
            priceInput.value = `${price.toFixed(2)}`;
            totalValueInput.value = `${(price * quantity).toFixed(2)}`;
        }
    }

    // Update price and total on stock change
    stockSelect.addEventListener("change", updatePriceAndTotal);

    // Update total when quantity changes
    quantityInput.addEventListener("input", updatePriceAndTotal);

    // Initialize with first stock price
    updatePriceAndTotal();
});

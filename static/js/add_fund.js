document.getElementById("addFundsForm").addEventListener("submit", function(event) {
    let amount = document.getElementById("amount").value;
    let cardNumber = document.getElementById("card_number").value;
    let expiry = document.getElementById("expiry").value;
    let cvv = document.getElementById("cvv").value;
    let errorMessage = document.getElementById("errorMessage");

    // Basic Validation
    if (amount <= 0) {
        errorMessage.textContent = "Please enter a valid amount.";
        event.preventDefault();
        return;
    }

    if (!/^\d{16}$/.test(cardNumber)) {
        errorMessage.textContent = "Invalid card number.";
        event.preventDefault();
        return;
    }

    if (!/^\d{2}\/\d{2}$/.test(expiry)) {
        errorMessage.textContent = "Invalid expiry date format.";
        event.preventDefault();
        return;
    }

    if (!/^\d{3}$/.test(cvv)) {
        errorMessage.textContent = "Invalid CVV.";
        event.preventDefault();
        return;
    }
});


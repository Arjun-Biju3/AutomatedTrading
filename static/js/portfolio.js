function toggleDropdown() {
    let dropdown = document.getElementById("dropdown-menu");
    dropdown.style.display = dropdown.style.display === "block" ? "none" : "block";
}

window.onclick = function(event) {
    if (!event.target.matches('#profile-img')) {
        document.getElementById("dropdown-menu").style.display = "none";
    }
}

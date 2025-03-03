document.addEventListener("DOMContentLoaded", function () {
    var profileImg = document.getElementById("profile-img");
    var dropdown = document.getElementById("dropdown-menu");

    profileImg.addEventListener("click", function () {
        dropdown.style.display = dropdown.style.display === "block" ? "none" : "block";
    });

    document.addEventListener("click", function (event) {
        if (!profileImg.contains(event.target) && !dropdown.contains(event.target)) {
            dropdown.style.display = "none";
        }
    });
});

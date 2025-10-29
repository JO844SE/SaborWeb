const check = document.getElementById("check");
const password = document.getElementById("password");

check.addEventListener("click", () => {
    if (check.checked) {
        password.type = "text";
    } else {
        password.type = "password";
    }
});

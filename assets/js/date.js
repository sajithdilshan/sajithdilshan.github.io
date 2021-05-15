function adjustAge() {
    document.getElementById("age").innerHTML = (new Date()).getFullYear() - (new Date(1990, 2, 26)).getFullYear();
}

function adjustCurrentYear() {
    document.getElementById("currentYear").innerHTML = (new Date()).getFullYear();
}

adjustAge()
adjustCurrentYear()
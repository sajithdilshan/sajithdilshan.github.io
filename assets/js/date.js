function adjustCurrentYear() {
    document.getElementById("currentYear").innerHTML = (new Date()).getFullYear();
}

adjustCurrentYear()
var check = function() {
    if (document.getElementById("password").value == document.getElementyById("confirm").value) {
        document.getElementById("message").innerHTML = "";
    } else {
        document.getElementById("message").innerHTML = "Passwords must match";
        document.getElementById("message").style.color = "red";
    }
}
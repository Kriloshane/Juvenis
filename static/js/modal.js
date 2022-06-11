    var modal = document.getElementById('mymodal');
    var btn = document.getElementById('mybtn')
    var span = document.getElementByClassName("close")[0];

    btn.onclick = function() {
    modal.style.display = "block";
    }
    span.onclick = function() {
    modal.style.display = "none";
    }
    window.onclick = function(e) {
    if (e.target == modal) {
    modal.style.display = "none";
    }
    }
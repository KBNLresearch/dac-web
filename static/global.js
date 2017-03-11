document.getElementById("other_input").onfocus = function(){
    document.getElementById("other_radio").checked = true;
};

function toggle(id) {
    var element = document.getElementById(id);
    if(element.style.display == "block") {
        element.style.display = "none";
    }
    else {
        element.style.display = "block";
    }
}
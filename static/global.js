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

function predict(url, ne) {
    var ajax_url = "predict";
    var ajax_url = ajax_url + "?url=" + url;
    var ajax_url = ajax_url + "&ne=" + encodeURIComponent(ne)

    $.ajax({
        type: "GET",
        url: ajax_url,
        success: function(data) {
            console.log(data);

            $('#reason').html(data.reason);

            var pred = 'none';
            if (data.link) {pred = data.link;}
            $('#prediction').html(pred);

            var p = 'none';
            if (data.prob) {p = data.prob;}
            $('#prob').html(p);

            if (data.candidates) {
                for (var res in data.candidates) {
                    var str = JSON.stringify(data.candidates[res].features);
                    str = str.replace(/,/g, '<br/>')
                        .replace(/:/g, ': ')
                        .replace('{', '<p>')
                        .replace('}', '</p>');
                    $('#feat_panel_' + res).html(str);
                }
            }
        }
    });

}

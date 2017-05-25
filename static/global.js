function toggle(id) {
    var element = document.getElementById(id);
    if(element.style.display == 'block') {
        element.style.display = 'none';
    }
    else {
        element.style.display = 'block';
    }
}

function predict(url, ne) {
    var ajax_url = 'predict';
    var ajax_url = ajax_url + '?url=' + url;
    var ajax_url = ajax_url + '&ne=' + encodeURIComponent(ne)

    $.ajax({
        type: 'GET',
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
                $('.candidate').each(function(i, obj) {
                    $(obj).find('.feat_panel').html('Not available');
                    for (var res in data.candidates) {
                        //console.log(data.candidates[res].id);
                        if (obj.id == data.candidates[res].id) {
                            console.log(obj.id);
                            var str = JSON.stringify(data.candidates[res].features);
                            str = str.replace(/,/g, '<br/>')
                                .replace(/:/g, ': ')
                                .replace('{', '<p>')
                                .replace('}', '</p>');
                            str = '<p>"prob": ' + data.candidates[res].prob +
                                '</p>' + str;
                            console.log(str);
                            $(obj).find('.feat_panel').html(str);
                        }
                    }
                });
            }

        }
    });

}

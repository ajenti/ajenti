$('.dashboard').live('sortstart', function () {
    $('#trash').fadeTo(500, 1);
});

$('.dashboard').live('sortstop', function () {
    $('#trash').fadeTo(500, 0).empty().text('Drop here to remove widget');
    $('#save-query').show();
    $('#save-query').animate({'height':'35px'}, 1000);
});

function dashboardSave() {
    var l = '';
    var r = '';

    $('#cleft > *').each(function(i,e) {
        l += $(e).attr('id') + ',';
    });
    $('#cright > *').each(function(i,e) {
        r += $(e).attr('id') + ',';
    });

    Ajenti.query('/handle/dashboard/save/'+l+'/'+r);
    return false;
}

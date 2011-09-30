var Ajenti;

var warning_button_id;


Ajenti = {
    selectCategory: function (id) {
        $('.ui-el-category').removeClass('selected');
        $('.ui-el-top-category').removeClass('selected');
        $('#'+id).addClass('selected');
        ajax('/handle/category/click/' + id);
        return false;
    },

    showAsModal: function (id) {
        $('#'+id).modal({show:true, backdrop:'static'}).center();
    },

    hideModal: function (id) {
        $('#'+id).modal('hide');
    },

    showWarning: function (text, btnid) {
        Ajenti.showAsModal('warningbox');
        $('#warning-text').html(text);
        $('#warningbox').addClass('modal');
        warning_button_id = btnid;
        $('.warning-button').click(Ajenti.acceptWarning);
        $('#warning-cancel-button').click(Ajenti.cancelWarning);
        return false;
    },

    cancelWarning: function () {
        $('#warningbox').modal('hide');
        return false;
    },

    acceptWarning: function () {
        Ajenti.cancelWarning();
        ajax('/handle/button/click/' + warning_button_id);
        return false;
    },

    toggleTreeNode: function (id) {
        $('*[id=\''+id+'\']').toggle();
        ajaxNoUpdate('/handle/treecontainer/click/'+id);

        x = $('*[id=\''+id+'-btn\']');
        if (x.attr('src').indexOf('/dl/core/ui/tree-minus.png') < 0)
            x.attr('src', '/dl/core/ui/tree-minus.png');
        else
            x.attr('src', '/dl/core/ui/tree-plus.png');

        return false;
    },
};



jQuery.fn.center = function () {
    this.css("top", (
        Math.max(
            ($(window).height() - this.outerHeight()) / 2,
            0
        ) + $(window).scrollTop()
    ) + "px");

    this.css("left", Math.max(0,(($(window).width() - this.outerWidth()) / 2) + $(window).scrollLeft()) + "px");
    return this;
}


function ui_showhide(id) {
    x = document.getElementById(id);
    if (x.style.display != 'none')
        x.style.display = 'none';
    else
        x.style.display = '';
}

function ui_show(id) {
    x = document.getElementById(id);
    x.style.display = '';
}

function ui_hide(id) {
    x = document.getElementById(id);
    x.style.display = 'none';
}

function noenter() {
    return !(window.event && window.event.keyCode == 13);
}

function ui_fill_custom_html(id, html) {
    document.getElementById(id).innerHTML = Base64.decode(html);
}


function ui_editable_activate(id) {
    $('#'+id+'-normal').hide();
    $('#'+id+'-active').show();
    return false;
}

function ui_editable_save(id) {
    ajaxForm(id, 'OK');
    return ui_editable_cancel(id);
}

function ui_editable_cancel(id) {
    $('#'+id+'-normal').show();
    $('#'+id+'-active').hide();
    return false;
}

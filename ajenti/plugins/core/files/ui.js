var Ajenti;

var warning_button_id


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
        $('#warning-button').click(Ajenti.acceptWarning);
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

function ui_treeicon(id) {
    x = document.getElementById(id);
    if (x.src.indexOf('/dl/core/ui/tree-minus.png') < 0)
        x.src = '/dl/core/ui/tree-minus.png';
    else
        x.src = '/dl/core/ui/tree-plus.png';
}

function ui_tabswitch(pid, id) {
    tc = 20;
    p = document.getElementById(pid);
    h = document.getElementById('tabheader-' + pid + '-' + id);
    b = document.getElementById('tabbody-' + pid + '-' + id);
    for (i=0;i<tc;i++)
        try {
            document.getElementById('tabheader-' + pid + '-' + i).setAttribute('class', 'ui-el-tab-header');
        } catch (err) { }
    h.setAttribute('class', 'ui-el-tab-header active');

    for (i=0;i<tc;i++)
        try {
            document.getElementById('tabbody-' + pid + '-' + i).style.display = 'none';
        } catch (err) { }
    b.style.display = '';

    while (p != null) {
        try {
            p = p.parentNode;
            if (p.getAttribute('class') == 'ui-el-modal-wrapper')
                ui_center_el(p);
        } catch (err) {
            break;
        }
    }
}

function noenter()
{
    return !(window.event && window.event.keyCode == 13);
}

function ui_fill_custom_html(id, html) {
    document.getElementById(id).innerHTML = Base64.decode(html);
}




function ui_help_setup(text) {
    hint = document.getElementById('help-hint');
    hint.innerHTML = text;
}

function ui_help_show(evt) {
    hint = document.getElementById('help-hint');
    hint.style.display = 'block';
    hint.style.left = (evt.clientX + window.pageXOffset + 10) + 'px';
    hint.style.top = (evt.clientY + window.pageYOffset + 10) + 'px';
}

function ui_help_hide() {
    hint = document.getElementById('help-hint');
    hint.style.display = 'none';
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

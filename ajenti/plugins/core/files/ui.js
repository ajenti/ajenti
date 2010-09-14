function ui_center_el(e) {
    sw = document.width;
    sh = document.height;
    e.style.left = (sw / 2 - e.clientWidth / 2) + 'px';
    e.style.top = (sh / 2 - e.clientHeight / 2) + 'px';
}

function ui_center(el) {
    ui_center_el(document.getElementById(el));
}

function ui_categoryfolder(id) {
    ui_showhide(id+'-children');
    x = document.getElementById(id);
    if (x.className == 'ui-el-categoryfolder')
        x.className = 'ui-el-categoryfolder-selected';
    else
        x.className = 'ui-el-categoryfolder';
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
    h.setAttribute('class', 'ui-el-tab-header-active');

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

function ui_hidewarning() {
    ui_hide('warningbox-all');
}

var warning_button_id

function accept_warning() {
    ui_hidewarning();
    ajax('/handle/button/click/' + warning_button_id);
}

function ui_showwarning(text, btnid) {
    ui_show('warningbox-all');
    ui_center('warningbox-wr');
    document.getElementById('warning-text').innerHTML = text;    
    warning_button_id = btnid;
    document.getElementById('warning-button').onclick = accept_warning;
}

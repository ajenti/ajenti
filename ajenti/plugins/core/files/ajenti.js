var Ajenti;

var warning_button_id;


Ajenti = {
    query: function (uri, data, noupdate) {
        $.ajax({
            url: uri,
            cache: false,   
            data: data,
            success: noupdate?undefined:Ajenti.Core.processResponse,
            error: Ajenti.Core.processOffline,
            method: data?'POST':'GET',
        });
        if (!noupdate)
            Ajenti.UI.showLoader(true);
        return false;
    },

    submit: function (fid, action) {
        form = $('#'+fid);
        if (form) {
            params = 'action=' + encodeURIComponent(action);
            url = $('input[type=hidden]', form)[0].value;

            $('input[type=text], input[type=password], input[type=hidden]', form).each(function (i,e) {
                params += '&' + e.name + '=' + encodeURIComponent(e.value);
            });

            $('input[type=checkbox]', form).each(function (i,e) {
                params += '&' + e.name + '=' + (e.checked?1:0);
            });

            $('input[type=radio]', form).each(function (i,e) {
                if (e.checked)
                    params += '&' + e.name + '=' + e.value;
            });

            $('select', form).each(function (i,e) {
                params += "&" + e.name + "=" + encodeURIComponent(e.options[e.selectedIndex].value);
            });

            $('textarea', form).each(function (i,e) {
                params += '&' + e.name + '=' + e.value;
            });

            $('.ui-el-sortlist', form).each(function (i,e) {
                var r = '';
                $('>*', $(e)).each(function(i,e) {
                    r += '|' + e.id;
                });
                params += '&' + e.id + '=' + r;
            });

            Ajenti.query(url, params);
        }
        return false;
    },

    init: function () {
        Ajenti.query('/handle/nothing');
        Ajenti.Core.requestProgress();
        Ajenti.UI.animateProgress();
    },

    Core: {
        processResponse: function (data) {
            $('.modal:not(#warningbox)').modal('hide').remove();
            $('.modal#warningbox').modal('hide');
            $('.modal-backdrop').fadeOut(500);
            $('.twipsy').remove();

            $('#rightplaceholder').empty();
            $('#rightplaceholder').html(data);
            $('#rightplaceholder script').each(function (i,e) {
                try {
                    eval($(e).text);
                } catch (err) { }
                $(e).text('');
            });
            Ajenti.UI.showLoader(false);
        },

        processOffline: function (data) {
            window.location.href = '/';
            Ajenti.UI.showLoader(false);
        },

        requestProgress: function () {
            $.ajax({
                url: '/core/progress',
                success: function (j) {
                    j = JSON.parse(j);
                    $('#progress-box').empty();
                    clearTimeout(Ajenti.UI._animateProgressTimeout);
                    for (prg in j) {
                        Ajenti.Core.addProgress(j[prg]);
                    }
                    Ajenti.UI.animateProgress();
                },
                complete: function () {
                    setTimeout('Ajenti.Core.requestProgress()', 3000);
                }
            });
        },

        addProgress: function (desc) {
            var html = '<div class="progress-box"><a class="close" onclick="return Ajenti.showWarning(\'';
            html += 'Cancel background task for ' + desc.owner + '?\', \'aborttask/' + desc.id + '\');">×</a>';
            html += '<p><strong>' + desc.owner + '</strong> ' + desc.status + '</p></div>';
            $('#progress-box').append(html);
        },

    },

    selectCategory: function (id) {
        $('.ui-el-category').removeClass('selected');
        $('.ui-el-top-category').removeClass('selected');
        $('#'+id).addClass('selected');
        Ajenti.query('/handle/category/click/' + id);
        return false;
    },

    showWarning: function (text, btnid) {
        Ajenti.UI.showAsModal('warningbox');
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
        Ajenti.query('/handle/button/click/' + warning_button_id);
        return false;
    },

    UI: {
        showAsModal: function (id) {
            $('#'+id).modal({show:true, backdrop:'static'}).center();
        },

        hideModal: function (id) {
            $('#'+id).modal('hide');
        },

        showLoader: function (visible) {
            if (visible) {
                $('#ajax-loader').show();
                $('body').css('cursor', 'wait !important');
            }
            else {
                $('#ajax-loader').hide();
                $('body').css('cursor', '');
            }
        },

        toggleTreeNode: function (id) {
            $('*[id=\''+id+'\']').toggle();
            Ajenti.query('/handle/treecontainer/click/'+id, null, true);

            x = $('*[id=\''+id+'-btn\']');
            if (x.attr('src').indexOf('/dl/core/ui/tree-minus.png') < 0)
                x.attr('src', '/dl/core/ui/tree-minus.png');
            else
                x.attr('src', '/dl/core/ui/tree-plus.png');

            return false;
        },

        editableActivate: function (id) {
            $('#'+id+'-normal').hide();
            $('#'+id).fadeIn(600);
            return false;
        },

        _animateProgressTimeout: null, 

        animateProgress: function () {
            var x = $('.progress-box').css('background-position-x');
            if (!x || x.length < 3) x = '0px';
            x = x.substr(0, x.length - 2);
            x = parseInt(x);
            $('.progress-box').css('background-position-x', x);
            $('.progress-box').stop().animate(
                {'background-position-x': x + 100}, 
                1000, 
                'linear'
            );
            Ajenti.UI._animateProgressTimeout = setTimeout('Ajenti.UI.animateProgress()', 1000);
        }
    }
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


function noenter() {
    return !(window.event && window.event.keyCode == 13);
}

function ui_fill_custom_html(id, html) {
    document.getElementById(id).innerHTML = Base64.decode(html);
}

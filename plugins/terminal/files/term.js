var _cursor, _cursx, _cursy;

function termSend(data) {
    $.ajax({
        url: '/term-post/' + data,
        type: 'GET',
        cache: false,
    });
}

function termGet(arg) {
    if (!arg) arg = '';

    $.ajax({
        url: '/term-get' + arg,
        type: 'GET',
        cache: false,
        success: function(data) {
            drawTerm(data);
            // Terminal is still here?
            if ($('#terminalplugin').hasClass('ui-el-category-selected'))
                setTimeout(function() {termGet()}, 1);
        }
    });
}

function drawTerm(d) {
    var data = JSON.parse(JXG.decompress(d));

    $('#term pre.cursor').removeClass('cursor');

    _cursor = data._cursor;
    if (data.cursor) {
        _cursx = data.cx;
        _cursy = data.cy;
    } else
        _cursx = -1;

    lns = $('#term div');
    for (k in data.lines) {
        if (lns.length <= k)
            $('#term').append(__row(data.lines[k], k));
        else {
            var ln = $(lns[k]);
            ln.html(__cells(data.lines[k], k));
        }
    }
}

function __cells(row, idx) {
    var r = '<pre>', fg, bg, bold, it, und, ch;
    for (var i=0; i<row.length; i++) {
        var cell = row[i];
        if (bg != cell[2] || fg != cell[1] || (idx == _cursy && i == _cursx) || (idx == _cursy && i == _cursx+1)) {
            var misc = '';
            if (idx == _cursy && i == _cursx)
                misc = ' class="cursor" ';
            if (cell[3] || cell[4] || cell[5]) {
                misc += ' style="';
                if (cell[3]) misc += 'font-weight: bold;';
                if (cell[4]) misc += 'font-style: italic;';
                if (cell[5]) misc += 'text-decoration: underline;';
                misc += '" ';
            }
            r += '</pre><pre' + misc + ' style="color:'+cell[1]+';background:'+cell[2]+';">';
            fg = cell[1];
            bg = cell[2];
            bold = cell[3];
            it = cell[4];
            und = cell[5];
        }
        ch = cell[0];
        if (ch == '<')
            ch = '&lt';
        if (ch == '>')
            ch = '&gt';
        r += cell[0];
    }
    r += '</pre>';
    return r;
}

function __row(row, idx) {
    return '<div>' + __cells(row, idx) + '</div>';
}

function termInit() {
    $('#capture').focus(function() {
        $(this).val('Input captured');
    });

    $('#capture').blur(function() {
        $(this).val('Input released');
    });

    _term = $('#term');


    $('#capture').keypress(function (event) {
        var ch = __filter_key(event);
        termSend(Base64.encode(ch));
    });

    setTimeout("termGet('-history')", 1000);
}


function __filter_key(event)
{
		ch = event.charCode;
    	if (event.ctrlKey) {
			ch = String.fromCharCode(event.keyCode - 64);
			return ch;
		}

		if (!ch && event.keyCode >= 112 && event.keyCode <= 123) { // F1-F12
		    ch = '\x1b' + (event.keyCode - 111);
		    return ch;
		}

		if (ch) {
			if (event.ctrlKey) {
				ch = String.fromCharCode(ch - 96);
			} else {
				ch = String.fromCharCode(ch);
				if (ch == '\r')
					ch = '\n';
			}
		} else {
			switch (event.keyCode) {
			    case 8:
				ch = '\b';
				break;
			    case 9:
				ch = '\t';
				break;
			    case 13:
			    case 10:
				ch = '\r';
				break;
			    case 38:
					ch = '\x1b[A';
				break;
			    case 40:
					ch = '\x1b[B';
				break;
			    case 39:
					ch = '\x1b[C';
				break;
			    case 37:
					ch = '\x1b[D';
				break;
			    case 46:
				ch = '\x1b[3~';
				break;
			    case 35: //end
				ch = '\x1b[F';
				break;
			    case 36: //home
			    ch = '\x1b[H';
				break;
			    case 34: //pgup
			    ch = '\x1b[6~';
				break;
			    case 33: //pgdown
			    ch = '\x1b[5~';
				break;
			    case 27:
				ch = '\x1b';
				break;
			    default:
				return '';
			}
		}
		event.preventDefault();
		return ch;
	}

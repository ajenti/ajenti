var _cursor, _cursx, _cursy, _tid;

function termInactivity() {
    $('#statusbox img').attr('src', '/dl/terminal/online.png');
    $('#statusbox span').css('color', '#888');
}

function termActivity() {
    $('#statusbox img').attr('src', '/dl/terminal/working.png');
    $('#statusbox span').text('online');
    setTimeout("termInactivity()", 200);
}

function termOffline() {
    $('#statusbox img').attr('src', '/dl/terminal/offline.png');
    $('#statusbox span').text('offline');
    $('#statusbox span').css('color', '#f98');
}

function termSend(data) {
    $.ajax({
        url: '/terminal/' + _tid + '/post/' + data,
        type: 'GET',
        cache: false,
        success: function () {
            termActivity();
        },
        error: termOffline
    });
}

function termGet(arg) {
    if (!arg) arg = 'get';

    $.ajax({
        url: '/terminal/' + _tid + '/' + arg,
        type: 'GET',
        cache: false,
        success: function(data) {
            drawTerm(data);
            setTimeout(function() {termGet()}, 1);
            termActivity();
        },
        error: termOffline
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

    $('#term').center();
}

function __cells(row, idx) {
    var r = '<pre>', fg=0, bg=0, bold=0, it=0, und=0, ch;
    for (var i=0; i<row.length; i++) {
        var cell = row[i];
        if (bg != cell[2] || fg != cell[1] || (idx == _cursy && i == _cursx) || (idx == _cursy && i == _cursx+1)) {
            var misc = '';
            var sty = '';
            if (idx == _cursy && i == _cursx)
                misc = ' class="cursor" ';
            if (cell[3] || cell[4] || cell[5]) {
                if (cell[3]) sty += 'font-weight: bold;';
                if (cell[4]) sty += 'font-style: italic;';
                if (cell[5]) sty += 'text-decoration: underline;';
            }
            r += '</pre><pre' + misc + ' style="color:'+cell[1]+';background:'+cell[2]+';'+sty+'">';
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

function termInit(tid) {
    _tid = tid;

    _term = $('#term');

    $(document).keypress(function (event) {
        var ch = __filter_key(event);
        if (event.which != 13)
            termSend(Base64.encode(ch));
        event.preventDefault();
    });

    $(document).keyup(function (event) {
        var ch = __filter_key(event);
        termSend(Base64.encode(ch));
        event.preventDefault();
    });

    setTimeout("termGet('history')", 1000);
}


function __filter_key(event) {
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




function termTV() {
    $('.tv-noise').css('width', document.width*2 + 'px');
    $('.tv-noise').css('height', document.height*2 + 'px');
    $('.tv-line').css('width', document.width*2 + 'px');
    termTVUpdate();
    termTVUpdateLine(true);
    termTVUpdateShake();
    $('.tv-icon').fadeOut();
}

function termTVUpdate() {
    $('.tv-noise').each(function (i,e) {
        var dx = Math.floor(Math.random()*50-25), dy = Math.floor(Math.random()*50-25);
        $(e).css('top', dx+'px');
        $(e).css('left', dy+'px');
    });

    $('.tv-line').each(function (i,e) {
        $(e).css('top', e.offsetTop + 3 + "px");
    });
    
    $('#term').css('opacity', 0.9+Math.random()*0.1+"");
    setTimeout("termTVUpdate()", 50);
}

function termTVUpdateLine(force) {
    $('.tv-line').each(function (i,e) {
        if (Math.random() > 0.25 && (force || e.offsetTop > $('#term')[0].offsetTop + $('#term')[0].clientHeight))
            $(e).css('top', $('#term')[0].offsetTop-Math.random()*500);
    });
    setTimeout("termTVUpdateLine()", 3000+Math.random()*4000);
}

function termTVUpdateShake(reset) {
    $('#term div').each(function (i,e) {
        var dx = Math.floor(Math.random()*5);
        if (reset) dx = 0;
        $(e).css('padding-left', dx+'px');
    });

    if (reset)
        setTimeout("termTVUpdateShake()", Math.random()*4000);
    else
        if (Math.random() < 0.20)
            setTimeout("termTVUpdateShake(true)", 20);
        else
            setTimeout("termTVUpdateShake()", 20);
}

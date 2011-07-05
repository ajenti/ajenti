var _cursor;

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
    
    lns = $('#term tr');
    for (k in data.lines) {
        if (lns.length <= k)
            $('#term table').append(__row(data.lines[k]));
        else {
            var ln = $(lns[k]);
            ln.empty();
            ln.append(__cells(data.lines[k]));
        }
    }
    
    if (data.cursor) {
        if (_cursor)
            $(_cursor).stop().css('opacity', 1);
        if ($('#term tr').length > 0) {
            cell = $('td', $('#term tr')[data.cy])[data.cx];
            _cursor = cell;
            blink(cell);
        }
    }
}

function blink( el ) {
    if (!el) {
        el = this;
    }
    $(el).animate( { opacity: 0 }, 800, function() {
        $(this).animate( {opacity: 0.5 }, 800, blink );
    } );
}

function __cell(chr) {
    return '<td style="color:'+chr[1]+';background:'+chr[2]+';">' + chr[0] + '</td>';
}

function __cells(row) {
    var r = '';
    for (var i=0; i<row.length; i++)
        r += __cell(row[i]);
    return r;
}

function __row(row) {   
    return '<tr>' + __cells(row) + '</tr>';
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

    $('#capture').keydown(function (event) {
        var ch = __filter_key(event);
        termSend(Base64.encode(ch));
    });
    
    onkey = function() {
        var vt = VT100.the_vt_;
 
        if (vt === undefined)
            return;
 
        var ch = vt.key_buf_.shift();
        if (ch === undefined)
            return;

        if (vt.echo_ && ch.length == 1)
            vt.addch(ch);
            
        termSend(Base64.encode(ch));
        _had_keypress = true;
    }

    termGet('-history');
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
			if (ch > 255)
				return '';
			if (event.ctrlKey && event.shiftKey) {
				// Don't send the copy/paste commands.
				var charStr = String.fromCharCode(ch);
				if (charStr == 'C' || charStr == 'V') {
					return '';
				}
			}
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
//					ch = '\x1bOA';
				break;
			    case 40:
					ch = '\x1b[B';
//					ch = '\x1bOB';
				break;
			    case 39:
					ch = '\x1b[C';
//					ch = '\x1bOC';
				break;
			    case 37:
					ch = '\x1b[D';
//					ch = '\x1bOD';
				break;
			    case 46:
				ch = '\x1b[3~';
				break; 
			    case 36: //end
				ch = '\x1b[H';
				break;
			    case 35: //home
			    ch = '\x1b[F';
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

function termProcess(data) {
    x = Base64.decode(data);
    _term.write(x);
    _term_box_element.scrollTop = 9000*9000;
}

function termSend(data) {
    $.ajax({
        url: '/term-post/' + data,
        type: 'GET',
        cache: false,
        success: termProcess
    });
}

function termGet(arg) {
    if (!arg) arg = '';
    
    $.ajax({
        url: '/term-get' + arg,
        type: 'GET',
        cache: false,
        success: function(data) {
            termProcess(data);
            // Terminal is still here?
            if (_term_box_element.parentNode != null)
                setTimeout(function() {termGet()}, 1);  
            else {
                // Restore keyboard controls
                _term.curs_set(false, false, _term_box_element);
            }
        }
    });  
}

function termInit() {
    _term_box_element = document.getElementById("term_box");
    _screen = document.getElementById("term");
        
    _term = new VT100(80, 24, "term", 1000);
       
    _term.debug_ = 1;
    _term.curs_set(true, true, _term_box_element);
    _term.noecho();

    _window_scroll_size = _term_box_element.scrollHeight;
    _term_box_element.style.height = _window_scroll_size + "px";

    VT100.go_getch_ = function() {
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

var logfilter_orig = null;

function ui_update_log_filter() {
    var el = document.getElementById("logfilter");
    var lg = document.getElementsByClassName("ui-el-logviewer")[0].children[0].children[0];

    if (!logfilter_orig)
        logfilter_orig = lg.innerHTML;

    if (el.value == "")
        lg.innerHTML = logfilter_orig;
        
    var lines = logfilter_orig.split("<");
    
    var r = "";
        
    for (i=0;i<lines.length;i++)
        if (lines[i].indexOf(el.value) != -1)
            r += "<" + lines[i];

    lg.innerHTML = r;
}
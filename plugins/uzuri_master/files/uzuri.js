function load_remote(id, url)
{
    var xmlReq = null;
    if(window.XMLHttpRequest)
	xmlReq = new XMLHttpRequest();
    else if(window.ActiveXObject)
	xmlReq = new ActiveXObject("Microsoft.XMLHTTP");
    if(xmlReq==null) return; // Failed to create the request

    xmlReq.id = id;
    show_host_status(id, "active");

    xmlReq.onreadystatechange = function()
    {
        if (xmlReq.readyState == 4)
        {
	    id = xmlReq.id;
	    if (xmlReq.status == 200) {
		obj = document.getElementById("remote-" + id);
		obj.innerHTML = xmlReq.responseText;
		try {
		    oo = obj.getElementsByClassName("ui-el-mainwindow-right")[0]
		    obj.innerHTML = oo.innerHTML
		} catch (err) { }
		eval_scripts(obj);
		show_host_status(id, "idle");
	    } else {
		show_host_status(id, "error");
	    }
        }
    }

    xmlReq.open ("GET", url, true);
    xmlReq.send (null);
    return false;
}

function eval_scripts(obj)
{
    var ob = obj.getElementsByTagName("script");
    for(var i=0; i<ob.length-1; i++)
        try {
            if(ob[i+1].text!=null) eval(ob[i+1].text);
        } catch (err) {}
}


function show_host_status(id, st)
{
    if (st == "idle")
	ui_show(id + "-icon-idle");
    else
	ui_hide(id + "-icon-idle");

    if (st == "active")
	ui_show(id + "-icon-active");
    else
	ui_hide(id + "-icon-active");

    if (st == "error")
	ui_show(id + "-icon-error");
    else
	ui_hide(id + "-icon-error");

    if (st == "warning")
	ui_show(id + "-icon-warning");
    else
	ui_hide(id + "-icon-warning");
}

function switch_host(id)
{
    var x = document.getElementById("uzuri-mainpane");
    for (i=0; i<x.children.length; i++)
	if (x.children[i].id != id)
	    ui_hide(x.children[i].id);
    ui_show(id);
}

function switch_host_num(num)
{
    var x = document.getElementById("uzuri-mainpane");
    for (i=0; i<x.children.length; i++)
	if (i == num)
	    ui_show(x.children[i].id);
	else
	    ui_hide(x.children[i].id);
}

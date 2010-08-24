var current_plugin = [];
var current_host = "";
var visible_host = "";
var hosts = [];
var cookies = [];

function load_hosts()
{
    var n = 0;
    var x = document.getElementById("uzuri-mainpane");
    for (i=0; i<x.children.length; i++)
	hosts[n++] = x.children[i].id.split('-')[2];
}

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
    update_activity(1);

    xmlReq.onreadystatechange = function()
    {
        if (xmlReq.readyState == 4)
        {
	    update_activity(-1);
	    id = xmlReq.id;
	    if (xmlReq.status == 200) {
		obj = document.getElementById("remote-" + id);
		obj.innerHTML = xmlReq.responseText;
		try {
		    oo = obj.getElementsByClassName("ui-el-mainwindow-right")[0]
		    obj.innerHTML = filter_page(oo.innerHTML)
		} catch (err) { }
		eval_scripts(obj);
		show_host_status(id, "idle");

		try {
		    current_plugin[id] = xmlReq.getResponseHeader("X-Uzuri-Plugin");
		    highlight_currents();
		} catch (err) { }
		try {
		    cookies[id] = xmlReq.getResponseHeader("X-Uzuri-Cookie");
		    ajaxNoUpdate("/uzuri/setcookie/" + id + "/" + cookies[id]);
		} catch (err) { }

	    } else {
		show_host_status(id, "error");
	    }
        }
    }


    xmlReq.open ("GET", url, true);

    try {
	xmlReq.setRequestHeader("X-Cookie", cookies[id]);
    } catch (err) { alert(err); }

    xmlReq.send (null);
    return false;
}

function repl(s, f, r)
{
    while (s.indexOf(f) >= 0)
	s = s.replace(f, r);
    return s;
}

function filter_page(html)
{
    html = repl(html, "ajax('/handle", "execute_query('/handle");
    html = repl(html, "ajaxForm('", "execute_query('/handle/form/submit/");
    return html;
}

function eval_scripts(obj)
{
    var ob = obj.getElementsByTagName("script");
    for(var i=0; i<ob.length; i++)
        try {
            if(ob[i].text!=null) eval(ob[i].text);
        } catch (err) {}
}

function switch_host(id)
{
    var x = document.getElementById("uzuri-mainpane");
    for (i=0; i<x.children.length; i++)
	if (x.children[i].id != id)
	    ui_hide(x.children[i].id);
    ui_show(id);
    current_host = id.split('-')[2];
    visible_host = current_host;
    highlight_currents();
}

function switch_host_num(num)
{
    var x = document.getElementById("uzuri-mainpane");
    for (i=0; i<x.children.length; i++)
	if (i == num) {
	    ui_show(x.children[i].id);
	    current_host = x.children[i].id.split('-')[2];
	    visible_host = current_host;
	} else
	    ui_hide(x.children[i].id);
    if (num == -1) {
	current_host = "all";
	visible_host = hosts[0];
	ui_show(x.children[0].id);
    }
    highlight_currents();
}

function set_cookie(host, cookie)
{
    cookies[host] = cookie;
}

function execute_query_single(hostid, url)
{
    load_remote(hostid, "/uzurigate/" + hostid + url);
}

function execute_query_all(url)
{
    for (i=0; i<hosts.length; i++)
	execute_query_single(hosts[i], url);
}

function execute_query(url)
{
    if (current_host != "all")
	execute_query_single(current_host, url);
    else
	execute_query_all(url);
}

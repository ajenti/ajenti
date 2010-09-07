var activity_left = 0;

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

    if (st == "desync")
	ui_show(id + "-icon-desync");
    else
	ui_hide(id + "-icon-desync");

    if (st == "warning")
	ui_show(id + "-icon-warning");
    else
	ui_hide(id + "-icon-warning");

    host_controlled[id] = (st == "idle" || st == "active");
    host_status[id] = st;
    update_counters();
}

function update_activity(dx)
{
    activity_left += dx;
    document.getElementById("activity-left").innerHTML = " " + activity_left;
    if (activity_left > 0) {
	ui_show("activity-shield");
	ui_show("activity-message");
    } else {
	ui_hide("activity-shield");
	ui_hide("activity-message");
    }
}


function highlight_currents()
{
    var x = document.getElementById("uzuri-sidepane");
    for (var i=0; i<x.children.length; i++) {
	e = x.children[i];
	if (e.className == "ui-el-category-selected")
	    e.className = "ui-el-category";
	if (e.id == ("plugin-" + current_plugin[visible_host]))
	    e.className = "ui-el-category-selected";
	if (e.id == ("remotebtn-" + current_host))
	    e.className = "ui-el-category-selected";
	if (e.id == "remoteallbtn" && current_host == "all")
	    e.className = "ui-el-category-selected";
    }
    update_counters();
}


function update_counters()
{
    var chid = "";
    var chc = 0;

    for (var i=0; i<hosts.length; i++)
	if (host_controlled[hosts[i]]) {
	    chid = hosts[i];
	    chc++;
	}

    s = "<span>Controlling</span> ";
    if (current_host == "all")
	if (chc == 1)
	    s += chid;
	else
	    s += chc + " hosts";
    else
	s += current_host;

    document.getElementById("uzuri-controlling").innerHTML = s;
    document.getElementById("uzuri-viewing").innerHTML = "<span>Viewing</span> " + visible_host;
}

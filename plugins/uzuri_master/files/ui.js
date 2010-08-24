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

    if (st == "warning")
	ui_show(id + "-icon-warning");
    else
	ui_hide(id + "-icon-warning");
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
    for (i=0; i<x.children.length; i++) {
	e = x.children[i];
	if (e.className == "uzuri-remote-plugin-button-active")
	    e.className = "uzuri-remote-plugin-button";
	if (e.className == "uzuri-remote-host-button-active")
	    e.className = "uzuri-remote-host-button";
	if (e.id == ("plugin-" + current_plugin[visible_host]))
	    e.className = "uzuri-remote-plugin-button-active";
	if (e.id == ("remotebtn-" + current_host))
	    e.className = "uzuri-remote-host-button-active";
	if (e.id == "remoteallbtn" && current_host == "all")
	    e.className = "uzuri-remote-host-button-active";
    }
}

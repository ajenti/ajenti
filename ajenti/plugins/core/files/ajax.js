function ajax(URL)
{
	xmlReq = null;
	if(window.XMLHttpRequest) 		xmlReq = new XMLHttpRequest();
	else if(window.ActiveXObject) 	xmlReq = new ActiveXObject("Microsoft.XMLHTTP");
	if(xmlReq==null) return; // Failed to create the request

    showAjaxLoader(true);

	xmlReq.onreadystatechange = function()
	{
		switch(xmlReq.readyState)
		{
		case 4:	// Done!
			ajaxHandler(xmlReq.responseText);
            showAjaxLoader(false);
			break;
		default:
			break;
		}
	}

// Make the request
	xmlReq.open ('GET', URL, true);
	xmlReq.send (null);
    return false;
}

function showAjaxLoader(s) {
    document.getElementById('ajax-loader').style.display = s ? 'block' : 'none';
    document.documentElement.style.cursor = s ? 'wait' : '';
}

function ajaxPOST(URL, params)
{
	xmlReq = null;
	if(window.XMLHttpRequest) 		xmlReq = new XMLHttpRequest();
	else if(window.ActiveXObject) 	xmlReq = new ActiveXObject("Microsoft.XMLHTTP");
	if(xmlReq==null) return; // Failed to create the request

    showAjaxLoader(true);

	xmlReq.onreadystatechange = function()
	{
		switch(xmlReq.readyState)
		{
		case 4:	// Done!
            showAjaxLoader(false);
			ajaxHandler(xmlReq.responseText);
			break;
		default:
			break;
		}
	}

	xmlReq.open ('POST', URL, true);
    xmlReq.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    xmlReq.setRequestHeader("Content-length", params.length);
    xmlReq.setRequestHeader("Connection", "close");
    xmlReq.send(params);
    return false;
}

function ajaxForm(formId, action)
{
    form = document.getElementById(formId);
    if (form)
    {
        params = "action=" + encodeURIComponent(action);

        var inputs = form.getElementsByTagName("input");
        url = inputs[0].value;
        if (inputs) {
            for (i=1; i<inputs.length; i++) {
                if (inputs[i].type == "text" || inputs[i].type == "password" || inputs[i].type == "hidden") {
                    params += "&" + inputs[i].name + "=" + encodeURIComponent(inputs[i].value);
                }
                if (inputs[i].type == "checkbox") {
                    if (inputs[i].checked)
                        params += "&" + inputs[i].name + "=1";
                    else
                        params += "&" + inputs[i].name + "=0";
                }
                if (inputs[i].type == "radio") {
                    if (inputs[i].checked) {
                        params += "&" + inputs[i].name + "=" + encodeURIComponent(inputs[i].value);
                    }
                }
            }
        }

        inputs = form.getElementsByTagName("select");
        if (inputs) {
            for (i=0; i<inputs.length; i++) {
                var sel = inputs[i];
                params += "&" + sel.name + "=" + encodeURIComponent(sel.options[sel.selectedIndex].value);
            }
        }

        inputs = form.getElementsByTagName("textarea");
        if (inputs) {
            for (i=0; i<inputs.length; i++) {
                var ta = inputs[i];
                params += "&" + ta.name + "=" + encodeURIComponent(ta.value);
            }
        }

        inputs = form.getElementsByClassName("ui-el-sortlist")[0];
        if (inputs) {
            params += "&" + inputs.id + "=" + ui_dumpSortList(inputs.id);
        }

        ajaxPOST(url, params);
    }
    return false;
}

function ajaxHandler(data)
{
	main = document.getElementById("rightplaceholder")
	$('.modal:not(#warningbox)').modal('hide').remove();
	$('.modal-backdrop').fadeOut(1000);
	$('.twipsy').remove();
	main.innerHTML = data
    var ob = main.getElementsByTagName("script");
    for(var i=0; i<ob.length; i++)
        try {
            if(ob[i].text!=null) { eval(ob[i].text);
                ob[i].text='';
            }
        } catch (err) {}
}

function ajaxNoUpdate(URL)
{
	xmlReq = null;
	if(window.XMLHttpRequest) 		xmlReq = new XMLHttpRequest();
	else if(window.ActiveXObject) 	xmlReq = new ActiveXObject("Microsoft.XMLHTTP");
	if(xmlReq==null) return; // Failed to create the request
	xmlReq.open ('GET', URL, true);
	xmlReq.send (null);
}

function scheduleRefresh(timeout)
{
    setTimeout("ajax('/handle/nothing')", timeout)
}

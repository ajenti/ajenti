function ajax(URL)
{
	xmlReq = null;
	if(window.XMLHttpRequest) 		xmlReq = new XMLHttpRequest();
	else if(window.ActiveXObject) 	xmlReq = new ActiveXObject("Microsoft.XMLHTTP");
	if(xmlReq==null) return; // Failed to create the request

	xmlReq.onreadystatechange = function()
	{
		switch(xmlReq.readyState)
		{
		case 4:	// Done!
			ajaxHandler(xmlReq.responseText);
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

function ajaxPOST(URL, params)
{
	xmlReq = null;
	if(window.XMLHttpRequest) 		xmlReq = new XMLHttpRequest();
	else if(window.ActiveXObject) 	xmlReq = new ActiveXObject("Microsoft.XMLHTTP");
	if(xmlReq==null) return; // Failed to create the request

	xmlReq.onreadystatechange = function()
	{
		switch(xmlReq.readyState)
		{
		case 4:	// Done!
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
        params = "action="+escape(action);

        var inputs = form.getElementsByTagName("input")
        if (inputs) {
            for (i=0; i<inputs.length; i++) {
                if (inputs[i].type == "text") {
                    params += "&" + inputs[i].name + "=" + escape(inputs[i].value);
                }
                if (inputs[i].type == "checkbox") {
                    if (inputs[i].checked) {
                        if (inputs[i].value) {
                            params += "&" + inputs[i].name + "=" + escape(inputs[i].value);
                        } else {
                            params += "&" + inputs[i].name + "=1";
                        }
                    } else {
                        params += "&" + inputs[i].name + "=";
                    }
                }
                if (inputs[i].type == "radio") {
                    if (inputs[i].checked) {
                        params += "&" + inputs[i].name + "=" + escape(inputs[i].value);
                    }
                }
            }
        }
        inputs = form.getElementsByTagName("select")
        if (inputs) {
            for (i=0; i<inputs.length; i++) {
                var sel = inputs[i];
                params += "&" + sel.name + "=" + escape(sel.options[sel.selectedIndex].value);
            }
        } 
        ajaxPOST(form.action, params);
    }
    return false;
}

function ajaxHandler(data)
{
	document.getElementById('main').innerHTML = data
    var ob = document.getElementsByTagName("script");
    for(var i=0; i<ob.length-1; i++)
        if(ob[i+1].text!=null) eval(ob[i+1].text);
    

	var re = new RegExp('update=([0-9]+)');
	var m = re.exec(data);
    if (m) 
        if (m[1] != 0)
		    setTimeout("ajax(\"/handle/update//\")", m[1])
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

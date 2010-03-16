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
		case 0:	// Uninitialized
			break;
		case 1: // Loading
			break;
		case 2: // Loaded
			break;
		case 3: // Interactive
			break;
		case 4:	// Done!
//			ajaxHandler(xmlReq.responseXML.getElementsByTagName('info')[0].firstChild.data,
//						xmlReq.responseXML.getElementsByTagName('data')[0].firstChild.data);
			ajaxHandler(xmlReq.responseText);
			break;
		default:
			break;
		}
	}

// Make the request
	xmlReq.open ('GET', URL, true);
	xmlReq.send (null);
}


function ajaxHandler(data)
{
	document.getElementById('main').innerHTML = data
	var re = new RegExp('update=([0-9]+)');
	var m = re.exec(data);
	if (m[1] != 0)
		setTimeout("ajax(\"/handle;update;;\")", m[1])
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
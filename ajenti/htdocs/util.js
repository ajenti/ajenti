function showhide(id) {
	x = document.getElementById(id);
	if (x.style.display != 'none') 
		x.style.display = 'none';
	else
		x.style.display = '';
}

function treeicon(id) {
	x = document.getElementById(id);
	if (x.src.indexOf('/dl;core;ui/tree-minus.png') < 0) 
		x.src = '/dl;core;ui/tree-minus.png';
	else
		x.src = '/dl;core;ui/tree-plus.png';
}

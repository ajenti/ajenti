function loadpage() {
	if (document.getElementById('main').childNodes[0].localName == 'script')
		ajax('/handle;;;')
}

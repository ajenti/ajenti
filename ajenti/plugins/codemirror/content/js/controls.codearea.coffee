class window.Controls.codearea extends window.Control
	createDom: () ->
		@dom = $("""
			<div class="control codearea"> 
			</div>
		""")
		@cm = CodeMirror @dom[0],
			value: @properties.value
			mode: @properties.mode
			lineNumbers: true
			matchBrackets: true
		@dom.find('>*').css(
			width:  @_int_to_px(@properties.width)
			height: @_int_to_px(@properties.height)
		)
		setTimeout @cm.refresh, 1

	detectUpdates: () ->
		r = {}
		value = @cm.getValue()
		if value != @properties.value
			r.value = value
		return r




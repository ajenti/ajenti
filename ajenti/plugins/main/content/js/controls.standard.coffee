class window.Controls.label extends window.Control
	createDom: () ->
		@dom = $("""<span class="control label">#{@properties.text}</span>""")


class window.Controls.button extends window.Control
	createDom: () ->
		@dom = $("""<a href="#" class="control button style-#{@properties.style}">#{@properties.text}</a>""")
		@dom.click (e) =>
			@event 'click'
			e.preventDefault()



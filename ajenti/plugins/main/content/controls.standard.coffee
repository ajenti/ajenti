class window.Controls.label extends window.Control
	createDom: () ->
		@dom = $("""<span>#{@properties.text}</span>""")


class window.Controls.button extends window.Control
	createDom: () ->
		@dom = $("""<a>#{@properties.text}</a>""")
		@dom.click () =>
			@event 'click'



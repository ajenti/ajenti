class window.Controls.label extends window.Control
	createDom: () ->
		@dom = $("""<span>#{@properties.text}</span>""")



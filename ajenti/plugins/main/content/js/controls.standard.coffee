class window.Controls.hc extends window.Control
	createDom: () ->
		@dom = $("""
			<div class="control hc"></div>
		""")
		@childContainer = @dom

	wrapChild: (child) ->
		return $('<div></div>').append(child.dom)


class window.Controls.vc extends window.Control
	createDom: () ->
		@dom = $("""
			<div class="control vc"></div>
		""")
		@childContainer = @dom

	wrapChild: (child) ->
		return $('<div></div>').append(child.dom)


class window.Controls.label extends window.Control
	createDom: () ->
		@dom = $("""<span class="control label">#{@properties.text}</span>""")


class window.Controls.button extends window.Control
	createDom: () ->
		@dom = $("""<a href="#" class="control button style-#{@properties.style}">#{@properties.text}</a>""")
		@dom.click (e) =>
			@event 'click'
			e.preventDefault()


class window.Controls.form extends window.Control
	createDom: () ->
		@dom = $("""
			<div><div class="--child-container"></div></div>
		""")
		@childContainer = @dom.find('.--child-container')


class window.Controls.textbox extends window.Control
	createDom: () ->
		@dom = $("""
			<div><input class="control textbox" type="text" value="#{@properties.value}" /></div>
		""")
		@input = @dom.find('input')

	detectUpdates: () ->
		r = {}
		if @input.val() != @properties.value
			r.value = @input.val()
		return r

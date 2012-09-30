_make_icon = (icon) ->
	if icon then """<i class="icon-#{icon}"></i>&nbsp;""" else ""



class window.Controls.default extends window.Control
	createDom: () ->
		@dom = $("""
			<div>
			</div>
		""")
		@childContainer = @dom


class window.Controls.pad extends window.Control
	createDom: () ->
		@dom = $("""
			<div class="control pad">
			</div>
		""")
		@childContainer = @dom


class window.Controls.box extends window.Control
	createDom: () ->
		w = if @properties.width  then (@properties.width  + 'px') else 'auto'
		h = if @properties.height then (@properties.height + 'px') else 'auto'
		@dom = $("""
			<div class="control box" style="width: #{w}; height: #{h}">
			</div>
		""")
		@childContainer = @dom


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


class window.Controls.icon extends window.Control
	createDom: () ->
		icon = _make_icon(@properties.icon)
		@dom = $("""<div class="control icon">#{icon}</div>""")


class window.Controls.button extends window.Control
	createDom: () ->
		icon = _make_icon(@properties.icon)
		@dom = $("""<a href="#" class="control button style-#{@properties.style}">#{icon}#{@properties.text}</a>""")
		@dom.click (e) =>
			@event 'click'
			e.preventDefault()


class window.Controls.formline extends window.Control
	createDom: () ->
		@dom = $("""
			<div class="control formline">
				<div class="control label">#{@properties.text}</div>
				<div class="--child-container">
				</div>
			</div>
		""")
		@childContainer = @dom.find('.--child-container')


class window.Controls.formgroup extends window.Control
	createDom: () ->
		@dom = $("""
			<div class="control formgroup">
				<div>#{@properties.text}</div>
				<div class="--child-container">
				</div>
			</div>
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
		value = @input.val()
		if @properties.type == 'integer'
			value = parseInt(value)
		if value != @properties.value
			r.value = value
		return r


class window.Controls.editable extends window.Control
	createDom: () ->
		icon = _make_icon(@properties.icon)
		@dom = $("""
			<div class="control editable">
				<div class="control label">#{icon} #{@properties.placeholder ? @properties.value}</div>
				<input class="control textbox" type="text" value="#{@properties.value}" />
			</div>
		""")
		@label = @dom.find('.label')
		@input = @dom.find('input')
		@input.hide()
		@label.click @goEditMode
		@input.blur @goViewMode
		@input.keyup (e) =>
			if e.which == 13
				@goViewMode()

	goViewMode: () =>
		@label.html(@properties.placeholder ? @input.val())
		@input.hide()
		@label.show()

	goEditMode: () =>
		@label.hide()
		@input.show()
		@input.focus()

	detectUpdates: () ->
		r = {}
		value = @input.val()
		if @properties.type == 'integer'
			value = parseInt(value)
		if value != @properties.value
			r.value = value
		return r


class window.Controls.checkbox extends window.Control
	createDom: () ->
		@dom = $("""
			<div class="control checkbox">
				<input 
					type="checkbox" 
					#{if @properties.value then 'checked="checked"' else ''} 
				/>
				<div class="control label">#{@properties.text}</div>
			</div>
		""")
		@input = @dom.find('input')

	detectUpdates: () ->
		r = {}
		checked = @input.is(':checked')
		if checked != @properties.value
			r.value = checked
		return r

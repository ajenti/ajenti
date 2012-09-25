class window.Controls.pad extends window.Control
	createDom: () ->
		@dom = $("""
			<div class="control pad">
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


class window.Controls.button extends window.Control
	createDom: () ->
		@dom = $("""<a href="#" class="control button style-#{@properties.style}">#{@properties.text}</a>""")
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


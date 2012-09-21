window.WEB_SOCKET_SWF_LOCATION = '/static/main/WebSocketMain.swf'


class Stream 
	constructor: () ->

	start: () ->
		@socket = io.connect('/stream')
		@socket.on 'ui', (ui) ->
			ui = JSON.parse(ui)
			console.log ui
			UI.replace(UI.inflate(ui))


class UIManager
	constructor: () ->
		@ui = null

	inflate: (json) ->
		children = []
		for child in json.children
			do (child) =>
				children.push @inflate(child)
		id = json.id.replace(':', '__')
		cls = Controls[id]
		return new cls(json, children)

	replace: (ui) ->
		@ui = ui
		$('body').empty().append(@ui.dom)


window.Stream = new Stream()
window.Stream.start()

window.UI = new UIManager()


window.Controls = { }


class window.Control
	constructor: (@properties, @children) ->
		@childContainer = null
		@dom = null
		console.log @properties, @children
		@createDom()
		for child in @children
			do (child) =>
				@append(child)
		console.log this

	createDom: () ->
		""

	append: (child) ->
		@childContainer.append(child.dom)

	remove: (child) ->
		child.remove()


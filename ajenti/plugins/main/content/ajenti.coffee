window.WEB_SOCKET_SWF_LOCATION = '/static/main/WebSocketMain.swf'


class Stream 
	constructor: () ->

	start: () ->
		@socket = io.connect('/stream')
		@socket.on 'ui', (ui) ->
			console.log ui

window.Stream = new Stream()
window.Stream.start()



window.Templates = { }
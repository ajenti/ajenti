class AjentiOrgConnector
    constructor: () ->
        if window.parent
            @target = window.parent
            @domainPolicy = '*'  # TODO!
            @enabled = true

    send: (event, data) ->
        if @enabled
            data ?= {}
            message = event: event, data: data
            @target.postMessage(message, @domainPolicy)

    reportHeight: (h) ->
        @send('height', h)


$ () ->
    window.aoConnector = new AjentiOrgConnector()
    window.aoConnector.send('ready')

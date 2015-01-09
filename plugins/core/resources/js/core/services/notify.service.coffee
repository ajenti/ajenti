angular.module('core').service 'notify', ($location, toaster) ->
    window.toaster = toaster
    @info = (title, text) ->
        toaster.pop('info', title, text)

    @success = (title, text) ->
        toaster.pop('success', title, text)

    @warning = (title, text) ->
        toaster.pop('warning', title, text)

    @error = (title, text) ->
        toaster.pop('error', title, text)

    @custom = (style, title, text, url) ->
        toaster.pop style, title, text, 5000, 'trustedHtml', () ->
            $location.path(url)

    return this

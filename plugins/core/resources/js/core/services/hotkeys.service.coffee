angular.module('core').service 'hotkeys', ($timeout, $window, $rootScope) ->
    @ESC = 27
    @ENTER = 13

    handler = (e, mode) ->
        isTextField = false
        if not e.metaKey and not e.ctrlKey
            if $('input:focus').length > 0 or $('textarea:focus').length > 0
                isTextField = true
        if e.which < 32
            char = e.which
        else
            char = String.fromCharCode(e.which)
        #console.log(char, e)
        if not isTextField
            $rootScope.$broadcast mode, char, e
        $rootScope.$broadcast "#{mode}:global", char, e
        $rootScope.$apply()
        return 

    $timeout () ->
        $(document).keydown (e) -> handler(e, 'keydown')
        $(document).keyup (e) -> handler(e, 'keyup')
        $(document).keypress (e) -> handler(e, 'keypress')

    @on = (scope, handler, mode) ->
        scope.$on (mode or 'keydown'), ($event, key, event) ->
            if handler(key, event)
                event.preventDefault()
                event.stopPropagation()
    return this
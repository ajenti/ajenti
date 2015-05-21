angular.module('core').service 'favicon', ($rootScope, identity, customization) ->
    @colors = {
        red:          '#F44336'
        bluegrey:     '#607D8B'
        purple:       '#9C27B0'
        blue:         '#2196F3'
        default:      '#2196F3'
        cyan:         '#00BCD4'
        green:        '#4CAF50'
        deeporange:   '#FF5722'
        orange:       '#FF9800'
        teal:         '#009688'
    }

    @set = (color) =>
        $rootScope.themeColorValue = @colors[color]
        
        canvas = document.createElement 'canvas'
        canvas.width = 16
        canvas.height = 16
        context = canvas.getContext('2d')
        if color
            context.fillStyle = @colors[color]
            #context.fillRect(4, 4, 8, 8)
            context.fillRect(4, 4, 3, 8)
            context.fillRect(4, 4, 8, 3)
            context.fillRect(9, 4, 3, 8)
            context.fillRect(4, 9, 8, 3)
        else
            # use this for something
            context.fillStyle = @colors[color]
            context.fillRect(1, 6, 4, 4)
            context.fillRect(6, 6, 4, 4)
            context.fillRect(11, 6, 4, 4)

        @setURL(canvas.toDataURL())

    @setURL = (url) ->
        link = $('link[rel="shortcut icon"]')[0]
        link.type = 'image/x-icon'
        link.href = url

    @init = () ->
        @scope = $rootScope.$new()
        @scope.identity = identity
        if customization.plugins.core.faviconURL
            @setURL(customization.plugins.core.faviconURL)
        else
            @scope.$watch 'identity.color', () =>
                @set(identity.color)

    return this
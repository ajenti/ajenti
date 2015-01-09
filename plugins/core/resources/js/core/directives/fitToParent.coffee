angular.module('core').directive 'fitToParent', () ->
    return ($scope, element, attrs) ->
        parent = element.parent()
    
        $(window).resize () ->
            if angular.isDefined attrs.fitWidth
                element.width(1)
                element.width(parent.width())
            if angular.isDefined attrs.fitHeight
                element.height(1)
                element.height(parent.height())                

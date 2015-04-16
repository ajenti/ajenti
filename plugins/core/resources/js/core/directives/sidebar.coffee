angular.module('core').directive 'coreSidebar', ($http, $log) ->
    return {
        restrict: 'E'
        scope: true
        template: '''
            <ng:include src="'/core:resources/partial/sidebarItem.html'" />
        '''
        link: ($scope, element, attrs) ->
            $http.get('/api/core/sidebar').success (data) ->
                $scope.item = data.sidebar
                $scope.item.expanded = true
                $scope.item.isRoot = true
                for item in $scope.item.children
                    item.expanded = true
                    item.isTopLevel = true
    }

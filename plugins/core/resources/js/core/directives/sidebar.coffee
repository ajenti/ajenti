angular.module('core').directive 'coreSidebar', ($http, $log) ->
    return {
        restrict: 'E'
        scope: true
        template: '''
            <div ng:bind-html="customization.plugins.core.sidebarUpperContent"></div>
            <ng:include src="'/core:resources/partial/sidebarItem.html'" />
            <div ng:bind-html="customization.plugins.core.sidebarLowerContent"></div>
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

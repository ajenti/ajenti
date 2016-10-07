angular.module('core').directive('coreSidebar', ($http, $log) =>
    ({
        restrict: 'E',
        scope: true,
        template: `
            <div ng:bind-html="customization.plugins.core.sidebarUpperContent"></div>
            <ng:include src="'/core:resources/partial/sidebarItem.html'" />
            <div ng:bind-html="customization.plugins.core.sidebarLowerContent"></div>
        `,
        link($scope, element, attrs) {
            $http.get('/api/core/sidebar').then(response => {
                $scope.item = response.data.sidebar;
                $scope.item.expanded = true;
                $scope.item.isRoot = true;
                $scope.item.children.forEach((item) => {
                    item.expanded = true;
                    item.isTopLevel = true;
                });
            });
        }
    })
);

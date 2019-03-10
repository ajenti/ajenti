angular.module('core').controller('CoreError404', function($scope, $location) {
    $scope.url = $location.$$absUrl;
});

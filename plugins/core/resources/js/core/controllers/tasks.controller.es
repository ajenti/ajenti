angular.module('core').controller('CoreTasksController', ($scope, socket, tasks, identity) => {
    $scope.tasks = tasks
});

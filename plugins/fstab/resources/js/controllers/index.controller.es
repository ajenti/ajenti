angular.module('ajenti.fstab').controller('FstabIndexController', function($scope, $http, pageTitle, gettext, notify) {
    pageTitle.set(gettext('Fstab'));

    $http.get('/api/get_mounted').then( (resp) => {
	    $scope.mounted = resp.data;
    });

    $http.get('/api/fstab').then( (resp) => {
	    $scope.python_get = resp.data;
    });

    $http.post('/api/fstab', {my_var: 'fstab'}).then( (resp) => {
	    $scope.python_post = resp.data;
    });

});


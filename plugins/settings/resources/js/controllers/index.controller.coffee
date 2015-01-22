angular.module('ajenti.settings').controller 'SettingsIndexController', ($scope, $http, notify, pageTitle, identity) ->
    pageTitle.set('Settings')

    $http.get('/api/settings/config').success (data) ->
        $scope.config = data
    .error () ->
        notify.error 'Could not load config'

    $scope.save = () ->
        $http.post('/api/settings/config', $scope.config).success (data) ->
            notify.success 'Saved'
        .error () ->
            notify.error 'Could not save config'

    $scope.availableColors = [
        'default'
        'bluegrey'
        'red'
        'deeporange'
        'orange'
        'green'
        'teal'
        'blue'
        'purple'
    ]

    $scope.$watch 'config.color', () ->
        identity.color = $scope.config.color

angular.module('ajenti.supervisor').controller 'SupervisorIndexController', ($scope, augeas, notify, pageTitle, passwd, services, gettext) ->
    pageTitle.set(gettext('Supervisor'))

    $scope.addProcess = (name) ->
        path = $scope.config.insert "program:#{$scope.newProcessName}", null
        $scope.config.insert path + '/command', 'true'
        $scope.newProcessName = ''

    $scope.extractName = (path) ->
        if not $scope.config or not path
            return null
        return $scope.config.getNode(path).name.split(':')[1]

    $scope.save = () ->
        augeas.set('supervisor', $scope.config).then () ->
            notify.success gettext('Saved')
        .catch (e) ->
            notify.error gettext('Could not save'), e.message

    $scope.reload = () ->
        augeas.get('supervisor').then (config) ->
            $scope.config = config
        $scope.processServices = {}
        services.getServices('supervisor').then (data) ->
            for service in data
                $scope.processServices[service.name] = service

    $scope.start = (name) ->
        services.runOperation($scope.processServices[name], 'start').then () ->
            $scope.reload()
        .catch (e) ->
            notify.error gettext('Failed'), e.message

    $scope.stop = (name) ->
        services.runOperation($scope.processServices[name], 'stop').then () ->
            $scope.reload()
        .catch (e) ->
            notify.error gettext('Failed'), e.message

    passwd.list().then (l) ->
        $scope.systemUsers = l

    $scope.reload()
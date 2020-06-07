angular.module('ajenti.check_certificates').controller 'CertIndexController', ($scope, $http, $interval, $timeout, notify, pageTitle, messagebox, gettext, config) ->
    pageTitle.set(gettext('Check certificates'))

    $scope.status = []

    config.getUserConfig().then (userConfig) ->
        $scope.userConfig = userConfig

        for url in $scope.userConfig.certificates.domain
            $http.post('/api/check_cert/test', {url:url}).then (resp) ->
                $scope.status.push(resp.data)

    $scope.add = () ->
        messagebox.prompt(gettext('New url')).then (msg) -> 
            if (!msg.value)
                return
            $http.post('/api/check_cert/test', {url:msg.value}).then (resp) ->
                    $scope.status.push(resp.data)
            $scope.userConfig.certificates.domain.push(msg.value)
            $scope.save()

    $scope.remove = (status) ->
        url = status.url
        messagebox.show({
            text: gettext('Remove the url ' + url + '?'),
            positive: gettext('Remove'),
            negative: gettext('Cancel')
        }).then () -> 
            index = $scope.userConfig.certificates.domain.indexOf(url)
            $scope.userConfig.certificates.domain.splice(index, 1)
            $scope.save()
            index = $scope.status.indexOf(status)
            $scope.status.splice(index, 1)

    $scope.save = () ->
        config.setUserConfig($scope.userConfig)

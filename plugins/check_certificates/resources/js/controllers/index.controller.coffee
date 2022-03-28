angular.module('ajenti.check_certificates').controller 'CertIndexController', ($scope, $http, $interval, $timeout, notify, pageTitle, messagebox, gettext, config) ->
    pageTitle.set(gettext('Check certificates'))

    $scope.status = []
    $scope.addNewVisible = false

    config.getUserConfig().then (userConfig) ->
        $scope.userConfig = userConfig
        $scope.userConfig.certificates = $scope.userConfig.certificates || {'domain': []}

        for url in $scope.userConfig.certificates.domain
            $http.post('/api/check_cert', {url:url}).then (resp) ->
                $scope.status.push(resp.data)

    $scope.openNew = () ->
        $scope.addNewVisible = true
        $scope.newUrl = ''
        $scope.newPort = 443

    $scope.closeNew = () ->
        $scope.addNewVisible = false

    $scope.add = () ->
        if !$scope.newPort
            $scope.newPort = 443
        url = "#{$scope.newUrl}:#{$scope.newPort}"
        $http.post('/api/check_cert', {url:url}).then (resp) ->
                $scope.status.push(resp.data)
        $scope.userConfig.certificates.domain.push(url)
        $scope.closeNew()
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

angular.module('ajenti.settings').controller 'SettingsIndexController', ($scope, $http, $sce, notify, pageTitle, identity, passwd) ->
    pageTitle.set('Settings')

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

    $scope.newClientCertificate =
        c: 'NA'
        st: 'NA'
        o: ''
        cn: ''

    identity.promise.then () ->
        $scope.newClientCertificate.o = identity.machine.name

        passwd.list().then (data) ->
            $scope.availableUsers = data

            $scope.$watch 'newClientCertificate.user', () ->
                $scope.newClientCertificate.cn = "#{identity.user}@#{identity.machine.hostname}"

            $scope.newClientCertificate.user = 'root'

    $http.get('/api/settings/config').success (data) ->
        $scope.config = data
    .error () ->
        $scope.config = {}
        notify.error 'Could not load config'

    $scope.save = () ->
        $http.post('/api/settings/config', $scope.config).success (data) ->
            notify.success 'Saved'
        .error () ->
            notify.error 'Could not save config'

    $scope.$watch 'config.color', () ->
        if $scope.config
            identity.color = $scope.config.color

    $scope.generateClientCertificate = () ->
        $scope.newClientCertificate.generating = true
        $http.post('/api/settings/generate-client-certificate', $scope.newClientCertificate).success (data) ->
            $scope.newClientCertificate.generating = false
            $scope.newClientCertificate.generated = true
            $scope.newClientCertificate.url = $sce.trustAsUrl("data:application/x-pkcs12;base64,#{data.b64certificate}")
            $scope.config.ssl.client_auth.certificates.push {
                user: $scope.newClientCertificate.user
                digest: data.digest
                name: data.name
                serial: data.serial
            }
        .error (err) ->
            $scope.newClientCertificate.generating = false
            $scope.newClientCertificateDialogVisible = false
            notify.error 'Certificate generation failed', err.message

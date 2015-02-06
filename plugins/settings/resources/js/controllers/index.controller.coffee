angular.module('ajenti.settings').controller 'SettingsIndexController', ($scope, $http, $sce, notify, pageTitle, identity, messagebox, passwd, settings) ->
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

    settings.getConfig().then (data) ->
        $scope.config = data
    .catch () ->
        $scope.config = {}
        notify.error 'Could not load config'

    $scope.$watch 'config.color', () ->
        if $scope.config
            identity.color = $scope.config.color

    $scope.save = () ->
        settings.setConfig($scope.config).then (data) ->
            notify.success 'Saved'
        .catch () ->
            notify.error 'Could not save config'

    $scope.createNewServerCertificate = () ->
        messagebox.show(
            title: 'Self-signed certificate'
            text: 'Generating a new certificate will void all existing client authentication certificates!'
            positive: 'Generate'
            negative: 'Cancel'
        ).then () ->
            $scope.config.ssl.client_auth.force = false
            notify.info 'Generating certificate', 'Please wait'
            $http.get('/api/settings/generate-server-certificate').success (data) ->
                notify.success 'Certificate successfully generated'
                $scope.config.ssl.enable = true
                $scope.config.ssl.certificate = data.path
                $scope.config.ssl.client_auth.certificates = []
                $scope.save()
            .error (err) ->
                notify.error 'Certificate generation failed', err.message

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

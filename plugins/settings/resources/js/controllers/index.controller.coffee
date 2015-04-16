angular.module('ajenti.settings').controller 'SettingsIndexController', ($scope, $http, $sce, notify, pageTitle, identity, messagebox, passwd, config, core) ->
    pageTitle.set('Settings')

    $scope.config = config

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

    config.load().then () ->
        config.getAuthenticationProviders().then (p) ->
            $scope.authenticationProviders = p
        .catch () ->
            notify.error 'Could not load authentication provider list'
    .catch () ->
        notify.error 'Could not load config'

    $scope.$watch 'config.color', () ->
        if config.data
            identity.color = config.data.color

    $scope.save = () ->
        config.save().then (data) ->
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
            config.data.ssl.client_auth.force = false
            notify.info 'Generating certificate', 'Please wait'
            $http.get('/api/settings/generate-server-certificate').success (data) ->
                notify.success 'Certificate successfully generated'
                config.data.ssl.enable = true
                config.data.ssl.certificate = data.path
                config.data.ssl.client_auth.certificates = []
                $scope.save()
            .error (err) ->
                notify.error 'Certificate generation failed', err.message

    $scope.generateClientCertificate = () ->
        $scope.newClientCertificate.generating = true
        $http.post('/api/settings/generate-client-certificate', $scope.newClientCertificate).success (data) ->
            $scope.newClientCertificate.generating = false
            $scope.newClientCertificate.generated = true
            $scope.newClientCertificate.url = $sce.trustAsUrl("data:application/x-pkcs12;base64,#{data.b64certificate}")
            config.data.ssl.client_auth.certificates.push {
                user: $scope.newClientCertificate.user
                digest: data.digest
                name: data.name
                serial: data.serial
            }
        .error (err) ->
            $scope.newClientCertificate.generating = false
            $scope.newClientCertificateDialogVisible = false
            notify.error 'Certificate generation failed', err.message

    $scope.addEmail = (email, username) ->
        config.data.auth.emails[email] = username
        $scope.newEmailDialogVisible = false

    $scope.removeEmail = (email) ->
        delete config.data.auth.emails[email]

    $scope.restart = () ->
        core.restart()

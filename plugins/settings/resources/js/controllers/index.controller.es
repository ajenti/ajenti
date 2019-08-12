angular.module('ajenti.settings').controller('SettingsIndexController', ($scope, $http, $sce, notify, pageTitle, identity, messagebox, passwd, config, core, locale, gettext) => {
    pageTitle.set(gettext('Settings'));

    $scope.config = config;
    $scope.oldCertificate = config.data.ssl.certificate;

    $scope.availableColors = [
        'default',
        'bluegrey',
        'red',
        'deeporange',
        'orange',
        'green',
        'teal',
        'blue',
        'purple'
    ];

    $scope.newClientCertificate = {
        c: 'NA',
        st: 'NA',
        o: '',
        cn: ''
    };

    identity.promise.then(() => {
        $scope.newClientCertificate.o = identity.machine.name;
        passwd.list().then((data) => {
            $scope.availableUsers = data;
            $scope.$watch('newClientCertificate.user', () => $scope.newClientCertificate.cn = `${identity.user}@${identity.machine.hostname}`);
            $scope.newClientCertificate.user = 'root';
        });
        $http.get('/api/core/languages').then(rq => $scope.languages = rq.data);
    });

    config.load().then(
        () => config.getAuthenticationProviders(config), () => notify.error(gettext('Could not load config'))
    ).then(p =>
        $scope.authenticationProviders = p
    ).catch(() =>
        notify.error(gettext('Could not load authentication provider list'))
    )

    $scope.$watch('config.data.color', () => {
        if (config.data) {
            identity.color = config.data.color;
        }
    });

    $scope.$watch('config.data.language', () => {
        if (config.data) {
            locale.setLanguage(config.data.language);
        }
    });

    $scope.save = () => {
        $scope.certificate = config.data.ssl.certificate;
        if ($scope.certificate != $scope.oldCertificate) {
            return  $http.post('/api/settings/test-certificate/', {'certificate': $scope.certificate})
                    .then(data => { config.save().then(dt => notify.success(gettext('Saved')))})
                    .catch(err => { notify.error(gettext('SSL Error')), err.message});
        }
        else {
            config.save().then(data =>
                notify.success(gettext('Saved'))
            ).catch(() =>
                notify.error(gettext('Could not save config')));
        }
    };

    $scope.createNewServerCertificate = () =>
        messagebox.show({
            title: gettext('Self-signed certificate'),
            text: gettext('Generating a new certificate will void all existing client authentication certificates!'),
            positive: gettext('Generate'),
            negative: gettext('Cancel')
        }).then(() => {
            config.data.ssl.client_auth.force = false;
            notify.info(gettext('Generating certificate'), gettext('Please wait'));
            return $http.get('/api/settings/generate-server-certificate').success(function(data) {
                notify.success(gettext('Certificate successfully generated'));
                config.data.ssl.enable = true;
                config.data.ssl.certificate = data.path;
                config.data.ssl.client_auth.certificates = [];
                $scope.save();
            })
            .error(err => notify.error(gettext('Certificate generation failed'), err.message));
        })
    ;

    $scope.generateClientCertificate = () => {
        $scope.newClientCertificate.generating = true;
        return $http.post('/api/settings/generate-client-certificate', $scope.newClientCertificate).success(function(data) {
            $scope.newClientCertificate.generating = false;
            $scope.newClientCertificate.generated = true;
            $scope.newClientCertificate.url = $sce.trustAsUrl(`data:application/x-pkcs12;base64,${data.b64certificate}`);
            config.data.ssl.client_auth.certificates.push({
                user: $scope.newClientCertificate.user,
                digest: data.digest,
                name: data.name,
                serial: data.serial
            });
        }).error((err) => {
            $scope.newClientCertificate.generating = false;
            $scope.newClientCertificateDialogVisible = false;
            notify.error(gettext('Certificate generation failed'), err.message);
        });
    };

    $scope.addEmail = (email, username) => {
        config.data.auth.emails[email] = username;
        $scope.newEmailDialogVisible = false;
    };

    $scope.removeEmail = email => delete config.data.auth.emails[email];

    $scope.restart = () => core.restart();
});

angular.module('ajenti.settings').controller('SettingsIndexController', ($scope, $http, $sce, notify, pageTitle, identity, messagebox, passwd, config, core, locale, gettext) => {
    pageTitle.set(gettext('Settings'));

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

    $scope.help_trusted_domains = gettext(
        "If Ajenti is installed behind a proxy, oder reachable by a fqdn other than provided by the host,\n" +
        "you can then specify the other domains here, and by this way avoiding some resources loading problems."
    )

    $scope.help_trusted_proxies = gettext(
        "If Ajenti is installed behind one or more proxies, specify the ip of these proxies here, in order to\n" +
        "get the real client ip address."
    )

    $scope.help_certificate = gettext(
        "This certificate is the default certificate used to create client certificate and to provide https connection.\n" +
        "Using a Let's Encrypt certificate here will break the client certificate generator.\n" +
        "Using a self-generated certificate is fine here."
    );

    $scope.help_fqdn_certificate = gettext(
        "If you have a special certificate for your domain, like a Let's Encrypt certificate, put it there.\n" +
        "If you are not sure, just use the same certificate as the one above."
    );

    $scope.provider_warning = () => {
        if ($scope.config.data.auth.provider != 'os') {
            notify.info(gettext('Please be sure to have at least one valid user in the authentication provider. When not, you will be lock out from Ajenti. '));
        }
    };

    $scope.add_trusted_proxy = () => {
        config.data.trusted_proxies.push("");
    };

    $scope.add_trusted_domain = () => {
        config.data.trusted_domains.push("");
    };

    $scope.delete_trusted_proxy = (proxy) => {
        messagebox.show({
            title: gettext(`Remove ${proxy}`),
            text: gettext(`Do you really want to remove the proxy ${proxy} from the list ?`),
            positive: gettext('Delete'),
            negative: gettext('Cancel')
        }).then(() => {
            pos = $scope.config.data.trusted_proxies.indexOf(proxy);
            $scope.config.data.trusted_proxies.splice(pos, 1);
            notify.success(gettext(`${proxy} removed`));
        });
    };

    $scope.delete_trusted_domain = (domain) => {
        messagebox.show({
            title: gettext(`Remove ${domain}`),
            text: gettext(`Do you really want to remove the domain ${domain} from the list ?`),
            positive: gettext('Delete'),
            negative: gettext('Cancel')
        }).then(() => {
            pos = $scope.config.data.trusted_domains.indexOf(domain);
            $scope.config.data.trusted_domains.splice(pos, 1);
            notify.success(gettext(`${domain} removed`));
        });
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
        () => {
            $scope.config = config;
            $scope.oldCertificate = $scope.config.data.ssl.certificate;
            config.getAuthenticationProviders(config).then(p =>
                $scope.authenticationProviders = p
            ).catch(() =>
                notify.error(gettext('Could not load authentication provider list'))
            );
        },
        () => notify.error(gettext('Could not load config'))
    )

    $scope.$watch('config.data.color', () => {
        if (config.data) {
            identity.color = config.data.color;
        }
    });

    $scope.getSmtpConfig = () => {
        config.getSmtpConfig().then((smtpConfig) => $scope.smtp_config = smtpConfig);
    };

    $scope.$watch('config.data.language', () => {
        if (config.data) {
            locale.setLanguage(config.data.language);
        }
    });

    $scope.save = () => {
        $scope.certificate = config.data.ssl.certificate;
        if ($scope.certificate != $scope.oldCertificate) {
            return  $http.post('/api/settings/test/ssl-certificate', {'certificate': $scope.certificate})
                    .then(data => { config.save().then(dt => notify.success(gettext('Saved')))})
                    .catch(err => { notify.error(gettext('SSL Error')), err.message});
        }
        else {
            config.save().then(data =>
                notify.success(gettext('Global config saved'))
            ).catch(() =>
                notify.error(gettext('Could not save global config')));
        };

        if ($scope.smtp_config) {
            config.setSmtpConfig($scope.smtp_config).then(data =>
                notify.success(gettext('Smtp config saved'))
            ).catch(() =>
                notify.error(gettext('Could not save smtp config')));
            }
        }

    $scope.createNewServerCertificate = () =>
        messagebox.show({
            title: gettext('Self-signed certificate'),
            text: gettext('Generating a new certificate will void all existing client authentication certificates!'),
            positive: gettext('Generate'),
            negative: gettext('Cancel')
        }).then(() => {
            config.data.ssl.client_auth.force = false;
            notify.info(gettext('Generating certificate'), gettext('Please wait'));
            return $http.post('/api/settings/generate/server-certificate').success(function(data) {
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
        return $http.post('/api/settings/generate/client-certificate', $scope.newClientCertificate).success(function(data) {
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

    $scope.showSMTPPassword = false;

    $scope.toggleShowSMTPPassword = () => $scope.showSMTPPassword = !$scope.showSMTPPassword;

    $scope.addEmail = (email, username) => {
        config.data.auth.emails[email] = username;
        $scope.newEmailDialogVisible = false;
    };

    $scope.removeEmail = email => delete config.data.auth.emails[email];

    $scope.restart = () => core.restart();
});

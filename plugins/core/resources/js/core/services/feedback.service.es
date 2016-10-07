angular.module('core').service('feedback', function($log, ajentiVersion, ajentiPlatform, ajentiPlatformUnmapped) {
    this.enabled = true; // TODO
    this.token = 'df4919c7cb869910c1e188dbc2918807';

    this.init = () => {
        mixpanel.init(this.token);
        mixpanel.register({
            version: ajentiVersion,
            platform: ajentiPlatform,
            platformUnmapped: ajentiPlatformUnmapped
        });
    };

    this.emit = (evt, params) => {
        if (this.enabled) {
            try {
                mixpanel.track(evt, params || {});
            } catch (e) {
                $log.error(e);
            }
        }
    };

    return this;
});

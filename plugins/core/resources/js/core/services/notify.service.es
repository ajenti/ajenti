angular.module('core').service('notify', function($location, toaster) {
    window.toaster = toaster;
    this.info = (title, text) => toaster.pop('info', title, text);

    this.success = (title, text) => toaster.pop('success', title, text);

    this.warning = (title, text) => toaster.pop('warning', title, text);

    this.error = (title, text) => toaster.pop('error', title, text);

    this.custom = (style, title, text, url) =>
        toaster.pop(style, title, text, 5000, 'trustedHtml', () => $location.path(url));

    return this;
});

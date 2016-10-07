angular.module('core').service('favicon', function($rootScope, identity, customization) {
    this.colors = {
        red:          '#F44336',
        bluegrey:     '#607D8B',
        purple:       '#9C27B0',
        blue:         '#2196F3',
        default:      '#2196F3',
        cyan:         '#00BCD4',
        green:        '#4CAF50',
        deeporange:   '#FF5722',
        orange:       '#FF9800',
        teal:         '#009688'
    };

    this.set = (color) => {
        $rootScope.themeColorValue = this.colors[color];

        let canvas = document.createElement('canvas');
        canvas.width = 16;
        canvas.height = 16;
        let context = canvas.getContext('2d');
        if (color) {
            context.fillStyle = this.colors[color];
            //context.fillRect(4, 4, 8, 8)
            context.fillRect(4, 4, 3, 8);
            context.fillRect(4, 4, 8, 3);
            context.fillRect(9, 4, 3, 8);
            context.fillRect(4, 9, 8, 3);
        } else {
            // use this for something
            context.fillStyle = this.colors[color];
            context.fillRect(1, 6, 4, 4);
            context.fillRect(6, 6, 4, 4);
            context.fillRect(11, 6, 4, 4);
        }

        this.setURL(canvas.toDataURL());
    };

    this.setURL = function(url) {
        let link = $('link[rel="shortcut icon"]')[0];
        link.type = 'image/x-icon';
        link.href = url;
    };

    this.init = function() {
        this.scope = $rootScope.$new();
        this.scope.identity = identity;
        if (customization.plugins.core.faviconURL) {
            this.setURL(customization.plugins.core.faviconURL);
        } else {
            this.scope.$watch('identity.color', () => {
                this.set(identity.color);
            });
        }
    };

    return this;
});

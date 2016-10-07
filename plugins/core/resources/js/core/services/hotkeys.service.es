angular.module('core').service('hotkeys', function($timeout, $window, $rootScope) {
    this.ESC = 27;
    this.ENTER = 13;

    let handler = function(e, mode) {
        let isTextField = false;
        if (!e.metaKey && !e.ctrlKey) {
            if ($('input:focus').length > 0 || $('textarea:focus').length > 0) {
                isTextField = true;
            }
        }

        var char = (e.which < 32) ? e.which : String.fromCharCode(e.which);
        if (!isTextField) {
            $rootScope.$broadcast(mode, char, e);
        }
        $rootScope.$broadcast(`${mode}:global`, char, e);
        $rootScope.$apply();
    };

    $timeout(() => {
        $(document).keydown(e => handler(e, 'keydown'));
        $(document).keyup(e => handler(e, 'keyup'));
        $(document).keypress(e => handler(e, 'keypress'));
    });

    this.on = (scope, handler, mode) =>
        scope.$on((mode || 'keydown'), ($event, key, event) => {
            if (handler(key, event)) {
                event.preventDefault();
                return event.stopPropagation();
            }
        });
    return this;
});

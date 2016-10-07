angular.module('core').directive('keyboardFocus', () =>
    ($scope, element, attrs) =>
        element.bind('keydown', (event) => {
            if (event.keyCode === 40) {
                element.find('*:focus').first().next().focus();
                event.preventDefault();
            }
            if (event.keyCode === 38) {
                element.find('*:focus').first().prev().focus();
                event.preventDefault();
            }
        })
);

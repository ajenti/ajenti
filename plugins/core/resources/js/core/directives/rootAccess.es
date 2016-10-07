angular.module('core').directive('rootAccess', identity =>
    ({
        restrict: 'A',
        link($scope, element, attr) {
            let template = `
                <div class="text-center root-access-blocker">
                    <h1>
                        <i class="fa fa-lock"></i>
                    </h1>
                    <h3 translate>
                        Superuser access required
                    </h3>
                </div>`;
            identity.promise.then(() => {
                if (!identity.isSuperuser) {
                    element.empty().append($(template));
                }
            });
        }
    })
);

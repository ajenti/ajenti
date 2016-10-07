angular.module('core').directive('messageboxContainer', (messagebox) =>
    ({
        restrict: 'E',
        template: `
            <dialog ng:show="message.visible" ng:repeat="message in messagebox.messages">
                <div class="modal-header">
                    <h4>{{message.title|translate}}</h4>
                </div>
                <div class="modal-body" ng:class="{scrollable: message.scrollable}">
                    <div ng:show="message.progress">
                        <progress-spinner></progress-spinner>
                    </div>
                    {{message.text|translate}}
                    <ng:include ng:if="message.template" src="message.template"></ng:include>
                    <div ng:show="message.prompt">
                        <label>{{message.prompt}}</label>
                        <input type="text" ng:model="message.value" ng:enter="doPositive(message)" class="form-control" autofocus />
                    </div>
                </div>
                <div class="modal-footer">
                    <a ng:click="doPositive(message)" ng:show="message.positive" class="positive btn btn-default btn-flat">{{message.positive|translate}}</a>
                    <a ng:click="doNegative(message)" ng:show="message.negative" class="negative btn btn-default btn-flat">{{message.negative|translate}}</a>
                </div>
            </dialog>`,
        link($scope, element, attrs) {
            $scope.messagebox = messagebox;

            $scope.doPositive = function(msg) {
                msg.q.resolve(msg);
                messagebox.close(msg);
            };

            $scope.doNegative = function(msg) {
                msg.q.reject(msg);
                messagebox.close(msg);
            };
        }
    })

);

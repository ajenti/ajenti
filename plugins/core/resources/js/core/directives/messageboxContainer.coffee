angular.module('core').directive 'messageboxContainer', (messagebox) ->
    return {
        restrict: 'E'
        template: '''
            <dialog ng:show="message.visible" ng:repeat="message in messagebox.messages">
                <div class="modal-header">
                    <h4>{{message.title}}</h4>
                </div>
                <div class="modal-body" ng:class="{scrollable: message.scrollable}">
                    <div ng:show="message.progress">
                        <progress-spinner></progress-spinner>
                    </div>
                    {{message.text}}
                    <ng:include ng:if="message.template" src="message.template"></ng:include>
                </div>
                <div class="modal-footer">
                    <a ng:click="doPositive(message)" ng:show="message.positive" class="positive btn btn-default btn-flat">{{message.positive}}</a>
                    <a ng:click="doNegative(message)" ng:show="message.negative" class="negative btn btn-default btn-flat">{{message.negative}}</a>
                </div>
            </dialog>
        '''
        link: ($scope, element, attrs) ->
            $scope.messagebox = messagebox

            $scope.doPositive = (msg) ->
                msg.q.resolve()
                messagebox.close(msg)

            $scope.doNegative = (msg) ->
                msg.q.reject()
                messagebox.close(msg)
    }

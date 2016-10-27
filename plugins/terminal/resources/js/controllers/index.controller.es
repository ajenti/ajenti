angular.module('ajenti.terminal').controller('TerminalIndexController', ($scope, $location, $q, pageTitle, terminals, gettext) => {
    pageTitle.set(gettext('Terminals'));

    $scope.refresh = () => {
        return terminals.list().then(function(list) {
            $scope.terminals = list;
        });
    };

    $scope.create = () => terminals.create().then(id => $location.path(`/view/terminal/${id}`));

    $scope.runCommand = () => terminals.create({command: $scope.command, autoclose: true}).then(id => $location.path(`/view/terminal/${id}`));

    $scope.kill = (terminal) => terminals.kill(terminal.id).then(() => $scope.refresh());

    $scope.refresh();
});

angular.module('ajenti.terminal').controller('ScriptWidgetController', ($scope, $location, notify, terminals, gettext) => {
    $scope.run = () => {
        let { script, input } = $scope.widget.config;
        if ($scope.widget.config.terminal) {
            terminals.create({command: script, autoclose: true}).then(id => $location.path(`/view/terminal/${id}`));
        } else {
            notify.info(gettext('Starting the script'), `${script.substring(0, 100)}...`);
            terminals.script({script, input}).then((data) => {
                if (data.code === 0) {
                    notify.success(gettext('Script has finished'), data.output + data.stderr);
                } else {
                    notify.warning(gettext('Script has failed'), data.stderr + data.output);
                }
            })
            .catch(err => notify.error(gettext('Could not launch the script'), err.message));
        }
    }
});

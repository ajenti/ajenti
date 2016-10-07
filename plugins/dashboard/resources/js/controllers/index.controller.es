angular.module('ajenti.dashboard').controller('DashboardIndexController', function($scope, $interval, gettext, notify, pageTitle, customization, messagebox, dashboard, config) {
    pageTitle.set(gettext('Dashboard'));

    $scope.ready = false;
    $scope._ = {};

    dashboard.getAvailableWidgets().then((data) => {
        $scope.availableWidgets = data;
        $scope.widgetTypes = {};
        data.forEach((w) => $scope.widgetTypes[w.id] = w);
    });

    $scope.addWidget = (index, widget) => {
        widget = {
            id: Math.floor(Math.random() * 0x10000000).toString(16),
            typeId: widget.id
        };
        $scope.userConfig.dashboard.tabs[index].widgetsLeft.push(widget);
        return $scope.save().then(() => {
            if (widget.config_template) {
                $scope.configureWidget(widget);
            }
            $scope.refresh();
        });
    };

    config.getUserConfig().then((userConfig) => {
        $scope.userConfig = userConfig;
        $scope.userConfig.dashboard = $scope.userConfig.dashboard || customization.plugins.dashboard.defaultConfig;

        if (!$scope.userConfig.dashboard.tabs) {
            $scope.userConfig.dashboard.tabs = [{
                name: 'Home',
                width: 2,
                widgetsLeft: $scope.userConfig.dashboard.widgetsLeft,
                widgetsRight: $scope.userConfig.dashboard.widgetsRight
            }];
            delete $scope.userConfig.dashboard['widgetsLeft'];
            delete $scope.userConfig.dashboard['widgetsRight'];
        }

        let updateInterval = $interval(() => $scope.refresh(), 1000);

        $scope.$on('$destroy', () => $interval.cancel(updateInterval));
    });

    $scope.onSort = () => $scope.save();

    $scope.refresh = () => {
        let rq = [];
        for (let tab of $scope.userConfig.dashboard.tabs) {
            for (let widget of tab.widgetsLeft.concat(tab.widgetsRight)) {
                rq.push({
                    id: widget.id,
                    typeId: widget.typeId,
                    config: widget.config || {}
                });
            }
        }
        dashboard.getValues(rq).then((data) => {
            $scope.ready = true;
            data.forEach((resp) => $scope.$broadcast('widget-update', resp.id, resp.data));
        });
    };

    $scope.addTab = (index) =>
        messagebox.prompt(gettext('New name')).then((msg) => {
            if (!msg.value) {
                return;
            }
            $scope.userConfig.dashboard.tabs.push({
                widgetsLeft: [],
                widgetsRight: [],
                name: msg.value
            });
            $scope.save();
        })
    ;

    $scope.removeTab = (index) =>
        messagebox.show({
            text: gettext(`Remove the '${$scope.userConfig.dashboard.tabs[index].name}' tab?`),
            positive: gettext('Remove'),
            negative: gettext('Cancel')
        }).then(() => $scope.userConfig.dashboard.tabs.splice(index, 1))
    ;

    $scope.renameTab = function(index) {
        let tab = $scope.userConfig.dashboard.tabs[index];
        messagebox.prompt(gettext('New name'), tab.name).then((msg) => {
            if (!msg.value) {
                return;
            }
            tab.name = msg.value;
            $scope.save();
        });
    };

    $scope.configureWidget = (widget) => {
        widget.config = widget.config || {};
        $scope.configuredWidget = widget;
    };

    $scope.saveWidgetConfig = () => {
        $scope.save().then(() => $scope.refresh());
        $scope.configuredWidget = null;
    };

    $scope.removeWidget = (tab, widget) => {
        tab.widgetsLeft.remove(widget);
        tab.widgetsRight.remove(widget);
        $scope.save();
    };

    $scope.save = () => config.setUserConfig($scope.userConfig);
});

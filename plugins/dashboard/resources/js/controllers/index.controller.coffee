angular.module('ajenti.dashboard').controller 'DashboardIndexController', ($scope, $interval, notify, pageTitle, dashboard, config) ->
    pageTitle.set('Dashboard')

    $scope.ready = false

    dashboard.getAvailableWidgets().then (data) ->
        $scope.availableWidgets = data
        $scope.widgetTypes = {}
        for w in data
            $scope.widgetTypes[w.id] = w

    $scope.addWidget = (w) ->
        widget =
            id: Math.floor(Math.random() * 0x10000000).toString(16)
            typeId: w.id
        $scope.userConfig.dashboard.widgetsLeft.push widget
        $scope.save().then () ->
            if w.config_template
                $scope.configureWidget(widget)
            $scope.refresh()

    config.getUserConfig().then (userConfig) ->
        $scope.userConfig = userConfig
        $scope.userConfig.dashboard ?= {
          widgetsLeft: [
            {
                id: 'w1'
                typeId: 'hostname'

            }
            {
                id: 'w2'
                typeId: 'cpu'
            }
            {
                id: 'w3'
                typeId: 'loadavg'
            }
          ]
          widgetsRight: [
            {
                id: 'w4'
                typeId: 'uptime'
            }
            {
                id: 'w5'
                typeId: 'memory'
            }
          ]
        }

        updateInterval = $interval () ->
            $scope.refresh()
        , 1000

        $scope.$on '$destroy', () ->
            $interval.cancel(updateInterval)

    $scope.onSort = () ->
        $scope.save()

    $scope.refresh = () ->
        rq = []
        for w in $scope.userConfig.dashboard.widgetsLeft.concat($scope.userConfig.dashboard.widgetsRight)
            rq.push {
                id: w.id
                typeId: w.typeId
                config: w.config or {}
            }
        dashboard.getValues(rq).then (data) ->
            $scope.ready = true
            for resp in data
                $scope.$broadcast 'widget-update', resp.id, resp.data

    $scope.configureWidget = (widget) ->
        widget.config ?= {}
        $scope.configuredWidget = widget

    $scope.saveWidgetConfig = () ->
        $scope.save().then () ->
            $scope.refresh()
        $scope.configuredWidget = null

    $scope.removeWidget = (widget) ->
        $scope.userConfig.dashboard.widgetsLeft.remove(widget)
        $scope.userConfig.dashboard.widgetsRight.remove(widget)
        $scope.save()

    $scope.save = () ->
        return config.setUserConfig($scope.userConfig)


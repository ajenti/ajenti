Dashboard Widgets
*****************

Example
=======

Basic example of a dynamic and configurable widget can be browsed and downloaded at https://github.com/ajenti/demo-plugins/tree/master/demo_5_widget

Plugins can provide dashboard widgets by extending the :class:`aj.plugins.dashboard.api.Widget` abstract class::

    @component(Widget)
    class RandomWidget(Widget):
        id = 'random'

        # display name
        name = 'Random'

        # template of the widget
        template = '/demo_5_widget:resources/partial/widget.html'

        # template of the configuration dialog
        config_template = '/demo_5_widget:resources/partial/widget.config.html'

        def __init__(self, context):
            Widget.__init__(self, context)

        def get_value(self, config):
            # generate value based on widget's config
            if 'bytes' not in config:
                return 'Not configured'
            return os.urandom(int(config['bytes'])).encode('hex')


There are some CSS classes available for the standard widget looks::

    <div ng:controller="Demo5WidgetController">
        <div class="widget-header">
            Random
        </div>
        <div class="widget-value">
            {{value || 'Unknown'}}
        </div>
    </div>



The templates should reference appropriate controllers::

    angular.module('ajenti.demo5').controller 'Demo5WidgetController', ($scope) ->
        # $scope.widget is our widget descriptor here
        $scope.$on 'widget-update', ($event, id, data) ->
            if id != $scope.widget.id
                return
            $scope.value = data


    angular.module('ajenti.demo5').controller 'Demo5WidgetConfigController', ($scope) ->
        # $scope.configuredWidget is our widget descriptor here
        # some defaults
        $scope.configuredWidget.config.bytes ?= 4


Initially, dashboard will create your widget with an empty (``{}``) config and show the configuration dialog you provided.

Dashboard will issue periodic requests to your :class:`aj.plugins.dashboard.api.Widget` implementations. Your widget classes should not retain any state. If user creates multiple widgets of same type, a single instance will be created to service their requests.

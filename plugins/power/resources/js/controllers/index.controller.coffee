angular.module('ajenti.power').controller 'PowerIndexController', ($scope, $interval, notify, pageTitle, power, messagebox) ->
    pageTitle.set('Power management')

    power.getUptime().then (uptime) ->
        $scope.uptime = uptime

        int = $interval () ->
            $scope.uptime += 1
        , 1000

        $scope.$on '$destroy', () ->
            $interval.cancel(int)

    power.getBatteries().then (batteries) ->
        $scope.batteries = batteries

    power.getAdapters().then (adapters) ->
        $scope.adapters = adapters

    $scope.poweroff = () ->
        messagebox.show(
            title: 'Warning'
            text: 'Machine will become unreachable. Continue?'
            positive: 'Shutdown'
            negative: 'Cancel'
        ).then () ->
            power.poweroff().then () ->
                messagebox.show progress: true, text: 'System is shutting down'

    $scope.reboot = () ->
        messagebox.show(
            title: 'Warning'
            text: 'Machine may become unreachable. Continue?'
            positive: 'Reboot'
            negative: 'Cancel'
        ).then () ->
            power.reboot().then () ->
                messagebox.show progress: true, text: 'System is rebooting. We will try to reconnect with it.'

    $scope.suspend = () ->
        messagebox.show(
            title: 'Warning'
            text: 'Machine will become unreachable. Continue?'
            positive: 'Suspend'
            negative: 'Cancel'
        ).then () ->
            power.suspend().then () ->
                messagebox.show progress: true, text: 'System is suspending'

    $scope.hibernate = () ->
        messagebox.show(
            title: 'Warning'
            text: 'Machine will become unreachable. Continue?'
            positive: 'Hibernate'
            negative: 'Cancel'
        ).then () ->
            power.hibernate().then () ->
                messagebox.show progress: true, text: 'System is hibernating'

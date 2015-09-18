angular.module('ajenti.filesystem').directive 'fileDialog', ($timeout, filesystem, notify, hotkeys, gettext) ->
    return {
        scope: {
            ngShow: "=?"
            onSelect: "&"
            onCancel: "&?"
            root: '=?'
            mode: '@?'
            name: '=?'
            path: '=?'
        }
        templateUrl: '/filesystem:resources/js/directives/fileDialog.html'
        link: ($scope, element, attrs) ->
            element.addClass('block-element')
            $scope.loading = false
            $scope.mode ?= 'open'
            $scope.path ?= '/'
            $scope.root ?= '/'

            $scope.navigate = (path, explicit) ->
                $scope.loading = true
                filesystem.list(path).then (data) ->
                    $scope.loadedPath = path
                    $scope.path = path
                    $scope.items = data.items
                    $scope.parent = data.parent
                    if $scope.path == $scope.root
                        $scope.parent = null
                    else if $scope.path.indexOf($scope.root) != 0
                        $scope.navigate($scope.root)
                    $scope.restoreFocus()
                .catch (data) ->
                    if explicit
                        notify.error gettext('Could not load directory'), data.message
                .finally () ->
                    $scope.loading = false

            $scope.select = (item) ->
                if item.isDir
                    $scope.navigate(item.path, true)
                else
                    if $scope.mode == 'open'
                        $scope.onSelect({path: item.path})
                    if $scope.mode == 'save'
                        $scope.name = item.name

            $scope.save = () ->
                $scope.onSelect({path: $scope.path + '/' + $scope.name})

            $scope.selectDirectory = () ->
                $scope.onSelect({path: $scope.path})

            hotkeys.on $scope, (char) ->
                if $scope.ngShow and char == hotkeys.ESC
                    $scope.onCancel()
                    return true

            $scope.restoreFocus = () ->
                setTimeout () ->
                    element.find('.list-group a').first().blur().focus()

            $scope.$watch 'ngShow', () ->
                if $scope.ngShow
                    $scope.restoreFocus()

            $scope.$watch 'root', () ->
                $scope.navigate($scope.root)

            $scope.$watch 'path', () ->
                if $scope.loadedPath != $scope.path
                    $scope.navigate($scope.path)
    }

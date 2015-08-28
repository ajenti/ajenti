angular.module('ajenti.filesystem').directive 'fileDialog', ($timeout, filesystem, notify, hotkeys) ->
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
        template: '''
            <dialog ng:show="ngShow">
                <div class="modal-header">
                    <h4 class="modal-title">
                        {{path}}
                    </h4>
                </div>
                <div class="modal-body file-open-dialog scrollable">
                    <progress-spinner ng:show="loading"></progress-spinner>
                    <div class="list-group" ng:hide="loading" keyboard-focus>
                        <a ng:show="parent" ng:click="navigate(parent)" href="#" class="list-group-item">
                            <i class="fa fa-fw fa-level-up"></i> Up one level
                        </a>
                        <a ng:click="select(item)" href="#" ng:repeat="item in items|orderBy:['-isDir', 'name']" class="list-group-item" ng:show="mode != 'directory' || item.isDir">
                            <i class="fa fa-fw" ng:class="::{'fa-folder-o': item.isDir, 'fa-file-o': item.isFile}"></i>
                            &nbsp;
                            {{::item.name}}
                            &nbsp;
                            <span class="subtle" ng:show="::item.isFile">{{::item.size|bytes}}</span>
                        </a>
                    </div>
                    <div ng:show="mode == 'save'">
                        <label>File name</label>
                        <input type="text" ng:model="$parent.name" class="form-control" required />
                    </div>
                </div>
                <div class="modal-footer">
                    <a ng:click="selectDirectory()" ng:show="mode == 'directory'" class="btn btn-primary btn-flat">Select this directory</a>
                    <a ng:click="save()" ng:show="mode == 'save'" ng:disabled="!name" class="btn btn-primary btn-flat">Save</a>
                    <a ng:click="onCancel()" class="btn btn-default btn-flat">Cancel</a>
                </div>
            </dialog>
        '''
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
                        notify.error 'Could not load directory', data.message
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

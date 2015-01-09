angular.module('util.filesystem').directive 'fileDialog', ($timeout, filesystem, notify, hotkeys) -> 
    return {
        scope: {
            ngShow: "=?"
            onSelect: "&"
            onCancel: "&?"
            mode: '@?'
            name: '=?'
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
                        <a ng:click="select(item)" href="#" ng:repeat="item in items|orderBy:['-isDir', 'name']" class="list-group-item">
                            <i class="fa fa-fw fa-folder-o" ng:if="item.isDir"></i>
                            <i class="fa fa-fw fa-file-o" ng:if="item.isFile"></i>
                            &nbsp;
                            {{item.name}}
                            &nbsp;
                            <span class="subtle" ng:show="item.isFile">{{item.size|bytes}}</span>
                        </a>
                    </div>
                    <div ng:show="mode == 'save'">
                        <label>File name</label>
                        <input type="text" ng:model="name" class="form-control" required />
                    </div>
                </div>            
                <div class="modal-footer">
                    <a ng:click="onCancel()" class="btn btn-default btn-flat">Cancel</a>
                    <a ng:click="save()" ng:show="mode == 'save'" ng:disabled="!name" class="btn btn-primary btn-flat">Save</a>
                </div>            
            </dialog>
        '''
        link: ($scope, element, attrs) ->
            element.addClass('block-element')
            $scope.loading = false
            $scope.mode ?= 'open'

            $scope.navigate = (path) ->
                $scope.loading = true
                filesystem.list(path).then (data) ->
                    $scope.path = path
                    $scope.items = data.items
                    $scope.parent = data.parent
                    $scope.restoreFocus()
                .catch () ->
                    notify.error 'Could not load directory'
                .finally () ->
                    $scope.loading = false

            $scope.select = (item) ->
                if item.isDir
                    $scope.navigate(item.path)
                else
                    if $scope.mode == 'open'
                        $scope.onSelect({item: item})
                    if $scope.mode == 'save'
                        $scope.name = item.name

            $scope.save = () ->
                $scope.onSelect({path: $scope.path + '/' + $scope.name})

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

            $scope.navigate('/')
    }

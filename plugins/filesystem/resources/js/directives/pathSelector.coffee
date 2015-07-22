angular.module('ajenti.filesystem').directive 'pathSelector', () ->
    return {
        restrict: 'E'
        scope: {
            ngModel: '='
            mode: '@'
        }
        template: """
            <div>
                <div class="input-group">
                    <input ng:model="ngModel" type="text" class="form-control" ng:required="attr.required" />
                    <span class="input-group-addon">
                        <a ng:click="openDialogVisible = true"><i class="fa fa-folder-open"></i></a>
                    </span>
                </div>
                <file-dialog
                    mode="{{mode}}"
                    path="path"
                    ng:show="openDialogVisible"
                    on-select="select(path)"
                    on-cancel="openDialogVisible = false" />
            </div>
        """
        link: ($scope, element, attr, ctrl) ->
            $scope.attr = attr
            $scope.path = '/'
            $scope.mode ?= 'open'

            $scope.select = (path) ->
                $scope.ngModel = path
                $scope.openDialogVisible = false

            $scope.$watch 'ngModel', () ->
                if $scope.ngModel
                    if $scope.mode == 'directory'
                        $scope.path = $scope.ngModel
                    else
                        $scope.path = $scope.ngModel.substr(0, $scope.ngModel.lastIndexOf('/'))
    }

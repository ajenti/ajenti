angular.module('ajenti.filesystem').directive 'pathSelector', () ->
    return {
        restrict: 'E'
        scope: {
            ngModel: '='
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
                    mode="open"
                    path="path"
                    ng:show="openDialogVisible"
                    on-select="select(item.path)"
                    on-cancel="openDialogVisible = false" />
            </div>
        """
        link: ($scope, element, attr, ctrl) ->
            $scope.attr = attr
            $scope.path = '/'

            $scope.select = (path) ->
                $scope.ngModel = path
                $scope.openDialogVisible = false

            $scope.$watch 'ngModel', () ->
                if $scope.ngModel
                    $scope.path = $scope.ngModel.substr(0, $scope.ngModel.lastIndexOf('/'))
    }

angular.module('ajenti.filesystem').directive( 'pathSelector', () =>
    ({
        restrict: 'E',
        scope: {
            ngModel: '=',
            mode: '@'
        },
        template: `<div>
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
</div>`,
        link($scope, element, attr, ctrl) {
            $scope.attr = attr;
            $scope.path = '/';
            if ($scope.mode == null) { $scope.mode = 'open'; }

            $scope.select = function(path) {
                $scope.ngModel = path;
                return $scope.openDialogVisible = false;
            };

            return $scope.$watch('ngModel', function() {
                if ($scope.ngModel) {
                    if ($scope.mode === 'directory') {
                        return $scope.path = $scope.ngModel;
                    } else {
                        return $scope.path = $scope.ngModel.substr(0, $scope.ngModel.lastIndexOf('/'));
                    }
                }
            }
            );
        }
    })

);

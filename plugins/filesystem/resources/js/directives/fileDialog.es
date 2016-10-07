angular.module('ajenti.filesystem').directive('fileDialog', ($timeout, filesystem, notify, hotkeys, identity, gettext) =>
    ({
        scope: {
            ngShow: "=?",
            onSelect: "&",
            onCancel: "&?",
            root: '=?',
            mode: '@?',
            name: '=?',
            path: '=?'
        },
        templateUrl: '/filesystem:resources/js/directives/fileDialog.html',
        link($scope, element, attrs) {
            element.addClass('block-element');
            $scope.loading = false;
            if ($scope.mode == null) { $scope.mode = 'open'; }
            if ($scope.path == null) { $scope.path = '/'; }

            $scope.navigate = function(path, explicit) {
                $scope.loading = true;
                return filesystem.list(path).then(function(data) {
                    $scope.loadedPath = path;
                    $scope.path = path;
                    $scope.items = data.items;
                    $scope.parent = data.parent;
                    if ($scope.path === $scope.root) {
                        $scope.parent = null;
                    } else if ($scope.path.indexOf($scope.root) !== 0) {
                        $scope.navigate($scope.root);
                    }
                    return $scope.restoreFocus();
                })
                .catch(function(data) {
                    if (explicit) {
                        return notify.error(gettext('Could not load directory'), data.message);
                    }
                })
                .finally(() => $scope.loading = false);
            };

            $scope.select = function(item) {
                if (item.isDir) {
                    return $scope.navigate(item.path, true);
                } else {
                    if ($scope.mode === 'open') {
                        $scope.onSelect({path: item.path});
                    }
                    if ($scope.mode === 'save') {
                        return $scope.name = item.name;
                    }
                }
            };

            $scope.save = () => $scope.onSelect({path: $scope.path + '/' + $scope.name});

            $scope.selectDirectory = () => $scope.onSelect({path: $scope.path});

            hotkeys.on($scope, function(char) {
                if ($scope.ngShow && char === hotkeys.ESC) {
                    $scope.onCancel();
                    return true;
                }
            }
            );

            $scope.restoreFocus = () =>
                setTimeout(() => element.find('.list-group a').first().blur().focus())
            ;

            return identity.promise.then(function() {
                if ($scope.root == null) { $scope.root = identity.profile.fs_root || '/'; }

                $scope.$watch('ngShow', function() {
                    if ($scope.ngShow) {
                        return $scope.restoreFocus();
                    }
                }
                );

                $scope.$watch('root', () => $scope.navigate($scope.root)
                );

                return $scope.$watch('path', function() {
                    if ($scope.loadedPath !== $scope.path) {
                        return $scope.navigate($scope.path);
                    }
                }
                );
            });
        }
    })

);

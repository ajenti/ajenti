angular.module('ajenti.cron').controller('CronIndexController', function($scope, $http, $log, pageTitle, gettext, notify, messagebox) {
    pageTitle.set(gettext('Cron'));

    $scope.title = gettext('Cron');
    $scope.modifyJob = null;
    $scope.new = {
        'normal_tasks': {
            'minute':'*',
            'hour':'*',
            'day_of_month':'*',
            'month':'*',
            'day_of_week':'*',
            'command':'',
            'comment':'',
            'new': true
        },
        'special_tasks': {
            'special': '@reboot',
            'command': '',
            'comment': '',
            'new': true
        },
        'env_settings': {
            'name': '',
            'value': '',
            'comment': '',
            'new': true
        }
    };

    $scope.translate = {
        'normal_tasks': gettext('normal task'),
        'special_tasks': gettext('special task'),
        'env_settings': gettext('environment variable')
    }
    $scope.special = ['@reboot', '@yearly', '@annually', '@monthly', '@weekly', '@daily', '@hourly']

    $scope.add = (type, values) => {
        job = angular.copy($scope.new[type]);
        $scope.modify(type, job);
    }

    $scope.remove = (type, values) => {
        messagebox.show({
            text: gettext('Do you really want to permanently delete this entry?'),
            positive: gettext('Delete'),
            negative: gettext('Cancel')
        }).then( () => {
            position = $scope.crontab[type].indexOf(values);
            $scope.crontab[type].splice(position, 1);
        })
    }

    $http.get('/api/crontab').then( (resp) => {
        $scope.crontab = resp.data;
    });

    $scope.modify = (type, job) => {
        $scope.modifyJob={'type':type,'job':job};
    }

    $scope.closeDialog = (type, job) => {
        if (job.new) {
            delete job.new;
            $scope.crontab[type].push(job);
        }
        $scope.modifyJob = null;
    }

    $scope.reset = () => {
        $scope.modifyJob = null;
    }

    $scope.save = () => {
        $http.post('/api/crontab', {'crontab': $scope.crontab}).then((resp) => {
            notify.success(gettext('Crontab successfully saved !'));
        }, error => {
            $log.log('Failed to save crontab', error);
            notify.error(gettext('Failed to save crontab'));
        });
    };

});


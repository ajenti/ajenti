angular.module('core').service('tasks', function($rootScope, $q, $http, notify, push, socket, gettext) {
    this.tasks = [];
    this.deferreds = {};

    $rootScope.$on('socket-event:connect', () => $http.get('/api/core/tasks/request-update'));

    $rootScope.$on('push:tasks', ($event, msg) => {
        if (msg.type === 'update') {
            if (this.tasks.length > msg.tasks.length) {
                this.tasks.length = msg.tasks.length;
            }

            for (let i = 0; i < msg.tasks.length; i++) {
                if (this.tasks.length <= i) {
                    this.tasks.push({});
                }
                angular.copy(msg.tasks[i], this.tasks[i]);
            }
        }
        if (msg.type === 'message') {
            if (msg.message.type === 'done') {
                var def = this.deferreds[msg.message.task.id];
                if (def) {
                    def.resolve();
                }
                notify.success(gettext(msg.message.task.name), gettext('Done'));
            }
            if (msg.message.type === 'exception') {
                var def = this.deferreds[msg.message.task.id];
                if (def) {
                    def.reject(msg.message);
                }
                return notify.error(gettext(msg.message.task.name), gettext(`Failed: ${msg.message.exception}`));
            }
        }
    });

    this.start = (cls, args, kwargs) => {
        args = args || [];
        kwargs = kwargs || {};

        let data = {
            cls,
            args,
            kwargs
        };
        return $http.post('/api/core/tasks/start', data).then(response => {
            let def = $q.defer();
            let taskId = response.data;
            this.deferreds[taskId] = def;

            return {id: taskId, promise: def.promise};
        })
    };

    return this;
});

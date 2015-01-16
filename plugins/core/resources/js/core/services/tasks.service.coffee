angular.module('core').service 'tasks', ($rootScope, notify, socket) ->
    @tasks = null

    socket.send('tasks', 'request-update')

    $rootScope.$on 'socket:tasks', ($event, msg) =>
        if msg.type == 'update'
            @tasks = msg.tasks
        if msg.type == 'message'
            if msg.message.type = 'done'
                notify.success 'Task finished', msg.message.task.name

    return this

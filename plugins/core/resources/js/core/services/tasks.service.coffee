angular.module('core').service 'tasks', ($rootScope, $q, $http, notify, socket) ->
    @tasks = []

    socket.send('tasks', 'request-update')

    $rootScope.$on 'socket:tasks', ($event, msg) =>
        if msg.type == 'update'
            #@tasks = msg.tasks
            if @tasks.length > msg.tasks.length
                @tasks.length = msg.tasks.length
            for i in [0...msg.tasks.length]
                if @tasks.length <= i
                    @tasks.push {}
                angular.copy msg.tasks[i], @tasks[i]
        if msg.type == 'message'
            if msg.message.type = 'done'
                console.log msg.message
                notify.success 'Task finished', msg.message.task.name

    @start = (cls, args, kwargs) ->
        args ?= []
        kwargs ?= {}
        data = {
            cls: cls
            args: args
            kwargs: kwargs
        }
        q = $q.defer()
        $http.post('/api/core/tasks/start', data).success () ->
            q.resolve()
        .error () ->
            q.reject()
        return q.promise

    return this

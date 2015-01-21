angular.module('core').service 'tasks', ($rootScope, $q, $http, notify, push, socket) ->
    @tasks = []

    $rootScope.$on 'socket-event:connect', () ->
        $http.get('/api/core/tasks/request-update')

    $rootScope.$on 'push:tasks', ($event, msg) =>
        if msg.type == 'update'
            #@tasks = msg.tasks
            if @tasks.length > msg.tasks.length
                @tasks.length = msg.tasks.length
            for i in [0...msg.tasks.length]
                if @tasks.length <= i
                    @tasks.push {}
                angular.copy msg.tasks[i], @tasks[i]
        if msg.type == 'message'
            console.log msg.message
            if msg.message.type == 'done'
                notify.success msg.message.task.name, 'Done'
            if msg.message.type == 'exception'
                notify.error msg.message.task.name, "Failed: #{msg.message.exception}"

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

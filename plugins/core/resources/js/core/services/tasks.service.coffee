angular.module('core').service 'tasks', ($rootScope, $q, $http, notify, push, socket) ->
    @tasks = []
    @deferreds = {}

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
            if @tasks.length == 0
                if $rootScope.toggleOverlayNavigation
                    $rootScope.toggleOverlayNavigation(false)
        if msg.type == 'message'
            if msg.message.type == 'done'
                def = @deferreds[msg.message.task.id]
                if def
                    def.resolve()
                notify.success msg.message.task.name, 'Done'
            if msg.message.type == 'exception'
                def = @deferreds[msg.message.task.id]
                if def
                    def.reject(msg.message)
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
        $http.post('/api/core/tasks/start', data).success (taskId) =>
            if $rootScope.toggleOverlayNavigation
                $rootScope.toggleOverlayNavigation(true)

            def = $q.defer()
            @deferreds[taskId] = def

            q.resolve(id: taskId, promise: def.promise)
        .error () ->
            q.reject()
        return q.promise

    return this

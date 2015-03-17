describe 'tasks service', () ->
    beforeEach () ->
        inject ($httpBackend, socket) ->
            socket.enabled = false
            $httpBackend.when('GET', '/api/core/tasks/request-update').respond {}
            $httpBackend.when('POST', '/api/core/tasks/start').respond {}

    afterEach () ->
        inject (socket) ->
            socket.enabled = true

    it 'inits', () ->
        inject ($rootScope, $httpBackend, tasks) ->
            $httpBackend.expectGET('/api/core/tasks/request-update')
            $rootScope.$broadcast 'socket-event:connect'
            $httpBackend.flush()

    it 'starts tasks', () ->
        inject ($rootScope, $httpBackend, tasks) ->
            $httpBackend.expectPOST('/api/core/tasks/start', {cls: 'cls', args: 'args', kwargs: 'kwargs'})
            p = tasks.start('cls', 'args', 'kwargs')
            assert.isFulfilled(p)
            $httpBackend.flush()

    it 'receives updates', () ->
        inject ($rootScope, $httpBackend, tasks) ->
            taskList = [
                {name: 'a'},
                {name: 'b'},
                {name: 'c'},
            ]
            $rootScope.$broadcast 'push:tasks', {
                type: 'update'
                tasks: taskList
            }
            expect(tasks.tasks[0].name).to.equal(taskList[0].name)
            expect(tasks.tasks[1].name).to.equal(taskList[1].name)

    it 'keeps task objects', () ->
        inject ($rootScope, tasks) ->
            taskList = [
                {name: 'a'},
                {name: 'b'},
            ]
            $rootScope.$broadcast 'push:tasks', {
                type: 'update'
                tasks: taskList
            }

            list1 = tasks.tasks
            task1 = tasks.tasks[0]

            taskList = [
                {name: 'c'},
            ]
            $rootScope.$broadcast 'push:tasks', {
                type: 'update'
                tasks: taskList
            }

            expect(list1).to.equal(tasks.tasks)
            expect(task1).to.equal(tasks.tasks[0])

    it 'receives messages', () ->
        inject ($rootScope, tasks, notify) ->
            @sinon.stub(notify, 'success')
            $rootScope.$broadcast 'push:tasks', {
                type: 'message'
                message: 
                    type: 'done'
                    task: {}
            }
            notify.success.should.have.been.calledWith()

            @sinon.stub(notify, 'error')
            $rootScope.$broadcast 'push:tasks', {
                type: 'message'
                message: 
                    type: 'exception'
                    task: {}
            }
            notify.error.should.have.been.calledWith()


describe 'core service', () ->
    beforeEach () ->
        inject ($httpBackend) ->
            $httpBackend.when('GET', '/api/core/restart-master').respond {}

    it 'forceRestart()', () ->
        inject ($httpBackend, $timeout, core) ->
            console.log '---'
            @sinon.stub(core, 'pageReload')
            $httpBackend.expectGET('/api/core/restart-master')
            p = core.forceRestart()
            $timeout.flush()
            $httpBackend.flush()
            assert.isFulfilled(p)

    it 'restart()', () ->
        inject ($q,$rootScope, core, messagebox) ->
            @sinon.stub(core, 'forceRestart')
            @sinon.stub messagebox, 'show', () ->
                q = $q.defer()
                q.resolve()
                return q.promise

            core.restart()
            $rootScope.$digest()

            core.forceRestart.should.have.been.calledWith()

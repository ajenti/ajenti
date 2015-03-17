describe 'core service', () ->
    beforeEach () ->
        inject ($httpBackend) ->
            $httpBackend.when('GET', '/api/core/restart-master').respond {}

    it 'forceRestart()', () ->
        inject ($httpBackend, $timeout, core) ->
            @sinon.stub(core, 'pageReload')
            p = core.forceRestart()
            $httpBackend.expectGET('/api/core/restart-master')
            $httpBackend.flush()
            $timeout.flush()
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

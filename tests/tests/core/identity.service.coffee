describe 'identity service', () ->
    beforeEach () ->
        module {
            ng:
                $window:
                    location: 
                        assign: sinon.stub()
        }
        __initHttpBackend()
        inject ($httpBackend) ->
            $httpBackend.when('GET', '/api/core/identity').respond {
                machine:
                    hostname: "test-box"
                    name: 'test box'
                identity: 
                    user: 'root'
                    effective: 0
            }
            $httpBackend.when('GET', '/api/core/logout').respond {}

    afterEach () ->
        inject ($httpBackend) ->
            $httpBackend.verifyNoOutstandingExpectation(false)
            $httpBackend.verifyNoOutstandingRequest(false)

    it 'inits', (done) ->
        angular.mock.inject ($httpBackend, identity) ->
            $httpBackend.expectGET('/api/core/identity')
            expect(identity.promise).to.be.fulfilled
            identity.promise.then () ->
                expect(identity.user).to.equal('root')
                expect(identity.effective).to.equal(0)
                done()
            $httpBackend.flush()

    it 'starts elevation', (done) ->
        angular.mock.inject ($httpBackend, $window, $timeout, identity) ->
            $httpBackend.expectGET('/api/core/logout')
            sinon.spy $window.location, 'assign'

            p = identity.elevate()
            p.then () ->
                $window.location.assign.should.have.been.calledWith()
                assert.isRejected(p)
                done()
            .finally () ->
            
            $timeout.flush(1000)
            $httpBackend.flush()

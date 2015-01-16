beforeEach () ->
    inject ($httpBackend) ->
        $httpBackend.when('GET', '/api/core/identity').respond {
            machine:
                hostname: "test-box"
                name: 'test box'
            identity: 
                user: 'root'
                effective: 0
        }

describe 'identity', () ->
    it 'works', (done) ->
        angular.mock.inject ($httpBackend, identity) ->
            expect(identity.promise).to.be.fulfilled
            identity.promise.then () ->
                expect(identity.user).to.equal('root')
                expect(identity.effective).to.equal(0)
                done()
            $httpBackend.expectGET('/api/core/identity')
            $httpBackend.flush()



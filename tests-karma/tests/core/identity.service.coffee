describe 'identity service', () ->
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
            $httpBackend.when('GET', '/api/core/logout').respond {}
            $httpBackend.when('POST', '/api/core/auth').respond (method, url, data, headers) ->
                data = JSON.parse(data)
                if data.username == 'root' and data.password == '123'
                    return [200, {success: true}]
                return [200, {success: false, error: 'error'}]

    it 'init()', (done) ->
        inject ($httpBackend, identity) ->
            identity.init()

            $httpBackend.expectGET('/api/core/identity')
            identity.promise.then () ->
                expect(identity.user).to.equal('root')
                expect(identity.effective).to.equal(0)
                done()

            assert.isFulfilled(identity.promise)
            $httpBackend.flush()

    it 'elevate()', (done) ->
        inject ($httpBackend, $window, $location, $timeout, urlPrefix, identity) ->
            $httpBackend.expectGET('/api/core/logout')
            @sinon.stub($window.location, 'assign')
            @sinon.stub($location, 'path').returns('/test')

            p = identity.elevate()
            p.then () ->
                $window.location.assign.should.have.been.calledWith("#{urlPrefix}/view/login/sudo:undefined//test")
                setTimeout () ->
                    done()

            assert.isFulfilled(p)
            $timeout.flush(1000)
            $httpBackend.flush()

    it 'auth() succeeds', (done) ->
        inject ($httpBackend, identity) ->
            $httpBackend.expectPOST('/api/core/auth')

            p = identity.auth('root', '123', 'normal')
            p.then () ->
                setTimeout () ->
                    done()

            assert.isFulfilled(p)
            $httpBackend.flush()

    it 'auth() fails', (done) ->
        inject ($httpBackend, identity) ->
            $httpBackend.expectPOST('/api/core/auth')

            p = identity.auth('root', 'boo', 'normal')
            p.catch () ->
                setTimeout () ->
                    done()

            assert.isRejected(p)
            $httpBackend.flush()

    it 'login()', () ->
        inject ($httpBackend, $location, $window, urlPrefix, identity) ->
            @sinon.stub($location, 'path').returns('/test')
            @sinon.stub($window.location, 'assign')

            identity.login()
            $window.location.assign.should.have.been.calledWith("#{urlPrefix}/view/login/normal//test")


    it 'logout()', (done) ->
        inject ($httpBackend, $window, $location, $timeout, urlPrefix, identity) ->
            $httpBackend.expectGET('/api/core/logout')
            @sinon.stub($window.location, 'assign')
            @sinon.stub($location, 'path').returns('/test')

            p = identity.logout()
            p.then () ->
                $window.location.assign.should.have.been.calledWith("#{urlPrefix}/view/login/normal//test")
                setTimeout () ->
                    done()

            assert.isFulfilled(p)
            $timeout.flush(1000)
            $httpBackend.flush()


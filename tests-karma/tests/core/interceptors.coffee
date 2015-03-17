describe 'unauthenticated interceptor', () ->
    beforeEach () ->
        inject ($httpBackend) ->
            $httpBackend.when('GET', '/test').respond () -> [401, {}]

    it "should redirect", (done) ->
        inject ($http, $window, $location, $httpBackend, notify, urlPrefix) ->
            @sinon.stub($window.location, 'assign')
            @sinon.stub($location, 'path').returns('/test')

            $http.get('/test').error () ->
                $window.location.assign.should.have.been.calledWith("#{urlPrefix}/view/login/normal//test")
                done()

            $httpBackend.flush()

    it "should be disableable", (done) ->
        inject ($rootScope, $http, $window, $location, $httpBackend, notify, urlPrefix) ->
            $rootScope.disableExpiredSessionInterceptor = true
            @sinon.stub($window.location, 'assign')
            @sinon.stub($location, 'path').returns('/test')

            $http.get('/test').error () ->
                $window.location.assign.should.not.have.been.calledWith("#{urlPrefix}/view/login/normal//test")
                done()

            $httpBackend.flush()


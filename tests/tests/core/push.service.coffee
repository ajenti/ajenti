describe 'push service', () ->
    it 'works', () ->
        inject ($rootScope, push) ->
            @sinon.spy($rootScope, '$broadcast')
            msg = {plugin: 'test', message: {}}
            $rootScope.$broadcast 'socket:push', msg
            $rootScope.$digest()
            $rootScope.$broadcast.should.have.been.calledWith('push:test', msg.message)

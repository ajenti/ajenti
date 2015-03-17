describe 'socket service', () ->
    it 'sends', () ->
        inject ($rootScope, socket) ->
            @sinon.stub(socket.socket, 'emit')
            data = {}
            socket.send('test', data)
            $rootScope.$digest()
            socket.socket.emit.should.have.been.calledWith('message', {plugin: 'test', data: data})

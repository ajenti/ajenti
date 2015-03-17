describe 'feedback service', () ->
    beforeEach ->
        window.mixpanel =
            init: () -> 0
            register: () -> 0
            track: () -> 0
       
    it 'inits', () ->
        inject (feedback) ->
            @sinon.stub(mixpanel, 'init')
            @sinon.stub(mixpanel, 'register')
            feedback.init()
            mixpanel.init.should.have.been.calledWith()
            mixpanel.register.should.have.been.calledWith()

    it 'emits events', () ->
        inject (feedback) ->
            @sinon.stub(mixpanel, 'track')

            feedback.init()
            feedback.emit('event', {a: 1})

            mixpanel.track.should.have.been.calledWith('event', {a: 1})

    it 'is disableable', () ->
        inject (feedback) ->
            @sinon.stub(mixpanel, 'track')

            feedback.init()
            feedback.enabled = false
            feedback.emit('event', {a: 1})
            mixpanel.track.should.not.have.been.calledWith()

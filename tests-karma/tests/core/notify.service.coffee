describe 'notify service', () ->
    for m in ['error', 'success', 'warning', 'info']
        do (m) ->
            it "#{m}()", () ->
                inject (toaster, notify) ->
                    @sinon.stub(toaster, 'pop')
                    notify[m]('title', 'text')
                    toaster.pop.should.have.been.calledWith(m, 'title', 'text')


    it "custom()", () ->
        inject (toaster, notify) ->
            @sinon.stub(toaster, 'pop')
            notify.custom('style', 'title', 'text')
            toaster.pop.should.have.been.calledWith('style', 'title', 'text')


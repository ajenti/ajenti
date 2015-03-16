describe 'pageTitle service', () ->
    it "sets", () ->
        inject ($rootScope, pageTitle) ->
            pageTitle.set('Test')
            $rootScope.$digest()
            expect($rootScope.pageTitle).to.equal('Test')

    it "sets from scope", () ->
        inject ($rootScope, pageTitle) ->
            scope = $rootScope.$new()
            scope.fx = () -> 'tes'
            pageTitle.set('fx() + "t"', scope)
            $rootScope.$digest()
            expect($rootScope.pageTitle).to.equal('test')

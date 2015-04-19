describe 'augeas service', () ->
    beforeEach () ->
        inject ($httpBackend) ->
            $httpBackend.when('GET', '/api/augeas/endpoint/get/test').respond {
                value: 'test'
                children: [
                    {
                        path: '/test/foo'
                        name: 'foo'
                        value: 1
                        children: []
                    }
                ]
                path: '/test'
            }
            $httpBackend.when('POST', '/api/augeas/endpoint/set/test').respond()

    it 'get()', (done) ->
        inject ($httpBackend, augeas) ->
            $httpBackend.expectGET('/api/augeas/endpoint/get/test')
            augeas.get('test').then (aug) ->
                expect(aug.root.value).to.equal('test')
                done()
            $httpBackend.flush()

    it 'set()', (done) ->
        inject ($httpBackend, augeas) ->
            $httpBackend.expectGET('/api/augeas/endpoint/set/test')
            $httpBackend.expectPOST('/api/augeas/endpoint/set/test')
            augeas.get('test').then (aug) ->
                augeas.set('test', aug).then () ->
                    done()
            $httpBackend.flush()

describe 'augeas config', () ->
    testTreeData = {
        path: '/test/root'
        name: 'root'
        value: null
        children: [
            {
                path: '/test/root/multi[1]'
                name: 'multi'
                value: 1
                children: []
            }
            {
                path: '/test/root/multi[2]'
                name: 'multi'
                value: 2
                children: [
                    {
                        path: '/test/root/multi[2]/single'
                        name: 'single'
                        value: 21
                        children: []
                    }
                ]
            }
            {
                path: '/test/root/multi[3]'
                name: 'multi'
                value: 3
                children: []
            }
            {
                path: '/test/root/extra'
                name: 'extra'
                value: 5
                children: []
            }
        ]
    }

    it 'loads', () ->
        inject (AugeasConfig) ->
            aug = AugeasConfig.get(testTreeData)
            expect(aug.root.value).to.equal(null)

    it 'match()', () ->
        inject (AugeasConfig) ->
            aug = AugeasConfig.get(testTreeData)
            expect(aug.match('/test/root/multi[2]')).to.deep.equal([
                '/test/root/multi[2]'
            ])
            expect(aug.match('/test/root/multi[5]')).to.deep.equal([])
            expect(aug.match('/test/root/multi[2]/single')).to.deep.equal([
                '/test/root/multi[2]/single'
            ])
            expect(aug.match('/test/root/ex.+')).to.deep.equal([
                '/test/root/extra'
            ])
            expect(aug.match('/test/root/multi')).to.deep.equal([
                '/test/root/multi[1]'
                '/test/root/multi[2]'
                '/test/root/multi[3]'
            ])

    it 'getNode()', () ->
        inject (AugeasConfig) ->
            aug = AugeasConfig.get(testTreeData)
            expect(aug.getNode('/test/root/nope')).to.equal(null)
            expect(aug.getNode('/test/root/multi[2]').value).to.equal(2)
            expect(aug.getNode('multi[2]').value).to.equal(2)

    it 'get()', () ->
        inject (AugeasConfig) ->
            aug = AugeasConfig.get(testTreeData)
            expect(aug.get('/test/root/nope')).to.equal(null)
            expect(aug.get('/test/root/multi[2]')).to.equal(2)
            expect(aug.get('multi[2]')).to.equal(2)

    it 'set()', () ->
        inject (AugeasConfig) ->
            aug = AugeasConfig.get(testTreeData)
            aug.set('/test/root/multi[2]', 55)
            expect(aug.get('/test/root/multi[2]')).to.equal(55)
            aug.set('multi[2]', 56)
            expect(aug.get('/test/root/multi[2]')).to.equal(56)
            aug.set('multi[2]/single', 56)
            expect(aug.get('/test/root/multi[2]/single')).to.equal(56)
            aug.set('multi[1]/new', 6)
            expect(aug.get('/test/root/multi[1]/new')).to.equal(6)

    it 'model()', () ->
        inject (AugeasConfig) ->
            aug = AugeasConfig.get(testTreeData)
            model = aug.model('/test/root/multi[1]')
            expect(model()).to.equal(1)
            model(2)
            expect(model()).to.equal(2)
            
    it 'remove()', () ->
        inject (AugeasConfig) ->
            aug = AugeasConfig.get(testTreeData)
            aug.remove('/test/root/multi[2]')
            expect(aug.match('/test/root/multi')).to.deep.equal([
                '/test/root/multi[1]'
                '/test/root/multi[2]'
            ])
            expect(aug.get('/test/root/multi[1]')).to.equal(1)
            expect(aug.get('/test/root/multi[2]')).to.equal(3)

    it 'insert()', () ->
        inject (AugeasConfig) ->
            aug = AugeasConfig.get(testTreeData)
            aug.insert('/test/root/multi', 4)
            expect(aug.get('/test/root/multi[4]')).to.equal(4)

            aug.insert('/test/root/multi', 99, 1)
            expect(aug.get('/test/root/multi[2]')).to.equal(99)

            aug.insert('/test/root/new', 1)
            expect(aug.get('/test/root/new')).to.equal(1)

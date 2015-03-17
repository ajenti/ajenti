describe 'rankMatch filter', () ->
    it 'works', () ->
        inject (rankMatchFilter) ->
            data = [ 
                {name: 'item one'}
                {name: 'item two'}
                {name: 'item three'}
                {name: 'item thirty one'}
            ]

            expect(rankMatchFilter(data, 'name', 'one')[0].rank).to.equal(1)
            expect(rankMatchFilter(data, 'name', 'one')[1].rank).to.equal(0)
            expect(rankMatchFilter(data, 'name', 'one')[2].rank).to.equal(0)
            expect(rankMatchFilter(data, 'name', 'one')[3].rank).to.equal(1)

            expect(rankMatchFilter(data, 'name', 'two')[0].rank).to.equal(0)
            expect(rankMatchFilter(data, 'name', 'two')[1].rank).to.equal(1)
            expect(rankMatchFilter(data, 'name', 'two')[2].rank).to.equal(0)
            expect(rankMatchFilter(data, 'name', 'two')[3].rank).to.equal(0) 

            expect(rankMatchFilter(data, 'name', 'item one')[0].rank).to.equal(61)
            expect(rankMatchFilter(data, 'name', 'item one')[3].rank).to.equal(0)

            expect(rankMatchFilter(null)).to.equal(null)


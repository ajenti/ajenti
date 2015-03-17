describe 'ordinal filter', () ->
    it 'works', () ->
        inject (ordinalFilter) ->
            expect(ordinalFilter(1)).to.equal('1st')
            expect(ordinalFilter(2)).to.equal('2nd')
            expect(ordinalFilter(3)).to.equal('3rd')
            expect(ordinalFilter(4)).to.equal('4th')
            expect(ordinalFilter(21)).to.equal('21st')
            expect(ordinalFilter(32)).to.equal('32nd')
            expect(ordinalFilter(43)).to.equal('43rd')
            expect(ordinalFilter(54)).to.equal('54th')
            expect(ordinalFilter(99)).to.equal('99th')
            expect(ordinalFilter(100)).to.equal('100th')
            expect(ordinalFilter(null)).to.equal(null)

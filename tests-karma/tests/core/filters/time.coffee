describe 'time filter', () ->
    it 'works', () ->
        inject (timeFilter) ->
            expect(timeFilter(0)).to.equal('00:00:00')
            expect(timeFilter(1)).to.equal('00:00:01')
            expect(timeFilter(61)).to.equal('00:01:01')
            expect(timeFilter(3661)).to.equal('01:01:01')
            expect(timeFilter(3661+3600*24)).to.equal('1d 01:01:01')
            expect(timeFilter(3661+3600*24*99)).to.equal('99d 01:01:01')
            expect(timeFilter(59+59*60+3600*23+3600*24*99)).to.equal('99d 23:59:59')

            expect(timeFilter(0, 2)).to.equal('00:00:00.00')
            expect(timeFilter(1.123, 2)).to.equal('00:00:01.12')
            expect(timeFilter(1.126, 2)).to.equal('00:00:01.12')

            expect(timeFilter(0, 0)).to.equal('00:00:00')

            expect(timeFilter(null)).to.equal('--:--:--')
            expect(timeFilter()).to.equal('--:--:--')

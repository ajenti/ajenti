describe 'page filter', () ->
    it 'works', () ->
        inject (pageFilter) ->
            data = [1,2,3,4,5,6,7,8,9]

            expect(pageFilter(data, 1, 3)).to.deep.equal([1,2,3])
            expect(pageFilter(data, 2, 3)).to.deep.equal([4,5,6])
            expect(pageFilter(data, 3, 3)).to.deep.equal([7,8,9])

            expect(pageFilter(data, 1, 1)).to.deep.equal([1])
            expect(pageFilter(data, 2, 1)).to.deep.equal([2])

            expect(pageFilter(data, 1, 99)).to.deep.equal(data)
            expect(pageFilter(data, 2, 99)).to.deep.equal([])

            expect(pageFilter(null)).to.equal(undefined)




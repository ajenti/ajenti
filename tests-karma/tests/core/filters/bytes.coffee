describe 'bytes filter', () ->
    it 'works', () ->
        inject (bytesFilter) ->
            expect(bytesFilter(0)).to.equal('0 bytes')
            expect(bytesFilter(2)).to.equal('2 bytes')
            expect(bytesFilter(512)).to.equal('512 bytes')
            expect(bytesFilter(1024)).to.equal('1.0 KB')
            expect(bytesFilter(1024 + 512)).to.equal('1.5 KB')
            expect(bytesFilter(1024 * 1024)).to.equal('1.0 MB')
            expect(bytesFilter(1024 * 1024 - 1)).to.equal('1024.0 KB')
            expect(bytesFilter(1024 * 1024 * 1024)).to.equal('1.0 GB')
            expect(bytesFilter(1024 * 1024 * 1024 * 1024)).to.equal('1.0 TB')
            expect(bytesFilter(1024 * 1024 * 1024 * 1024 * 1024)).to.equal('1.0 PB')

            expect(bytesFilter(123123, 3)).to.equal('120.237 KB')
            expect(bytesFilter(1024 * 1024, undefined)).to.equal(bytesFilter(1024 * 1024, 1))

            expect(bytesFilter(undefined)).to.equal('-')
            expect(bytesFilter(1/0)).to.equal('-')


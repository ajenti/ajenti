angular.module('core').filter 'bytes', () ->
    return (bytes, precision) ->
        if isNaN(parseFloat(bytes)) or !isFinite(bytes)
            return '-'
        if bytes == 0
            return '0 bytes'
        if typeof precision == 'undefined'
            precision = 1
        units = ['bytes', 'KB', 'MB', 'GB', 'TB', 'PB']
        number = Math.floor(Math.log(bytes) / Math.log(1024))

        x = (bytes / Math.pow(1024, Math.floor(number)))
        if number == 0
            x = Math.floor(x)
        else
            x = x.toFixed(precision)

        return x +  ' ' + units[number]


angular.module('core').filter 'ordinal', () ->
    return (input) ->
        if isNaN(input) or input == null
            return input

        s = ["th", "st", "nd", "rd"]
        v = input % 100
        return input + (s[(v - 20) % 10] or s[v] or s[0])


angular.module('core').filter 'page', () ->
    return (list, page, pageSize) ->
        if list and pageSize
            return list.slice((page - 1) * pageSize, page * pageSize)


angular.module('core').filter 'rankMatch', () ->
    return (input, field, query) ->
        if not input
            return input
        rgx = new RegExp(query, 'gi')
        for item in input
            points = 0
            data = item[field]
            points += (data.match(rgx) or []).length
            if data == query
                points += 50
            if data.indexOf(query) == 0
                points += 10
            item.rank = points
        return input


angular.module('core').filter 'time', () ->
    return (time, frac) ->
        if time == null or not angular.isDefined(time)
            return '--:--:--'
        s = ''
        if time >= 3600 * 24
            s += Math.floor(time / 3600 / 24) + ':'
        s += ('' + Math.floor(time / 60 / 60) % 24).lpad('0', 2) + ':'
        s += ('' + Math.floor(time / 60) % 60).lpad('0', 2) + ':'
        s += ('' + Math.floor(time) % 60).lpad('0', 2)
        if frac
            s += '.' + ('' + Math.floor((time - Math.floor(time)) * Math.pow(10, frac))).lpad('0', frac + 0)
        return s


class Profiler
    constructor: () ->
        @profiles = {}
        @results = {}
        @timeout = null
        @stack = []

    start: (id) ->
        if @profiles[id]
            @stack.push null
        else
            @profiles[id] ?= new Date().getTime()
            @stack.push id

    stop: (id) ->
        id ?= @stack.pop()
        if id == null
            return
        @results[id] ?= 0.0
        @results[id] += new Date().getTime() - @profiles[id]
        @profiles[id] = undefined

        clearTimeout @timeout
        @timeout = setTimeout () => 
            @dump()
        , 1000

    dump: () ->
        for id of @results
            console.log 'Profiled', id, @results[id] / 1000, 's'
        @results = {}


window.profiler = new Profiler()

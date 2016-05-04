angular.module('ajenti.filesystem').service 'filesystem', ($http, $q) ->
    @mountpoints = () ->
        q = $q.defer()
        $http.get("/api/filesystem/mountpoints").success (data) ->
            q.resolve(data)
        .error (err) ->
            q.reject(err)
        return q.promise

    @read = (path, encoding) ->
        q = $q.defer()
        $http.get("/api/filesystem/read/#{path}?encoding=#{encoding or 'utf-8'}").success (data) ->
            q.resolve(data)
        .error (err) ->
            q.reject(err)
        return q.promise

    @write = (path, content, encoding) ->
        q = $q.defer()
        $http.post("/api/filesystem/write/#{path}?encoding=#{encoding or 'utf-8'}", content).success (data) ->
            q.resolve(data)
        .error (err) ->
            q.reject(err)
        return q.promise

    @list = (path) ->
        q = $q.defer()
        $http.get("/api/filesystem/list/#{path}").success (data) ->
            q.resolve(data)
        .error (err) ->
            q.reject(err)
        return q.promise

    @stat = (path) ->
        q = $q.defer()
        $http.get("/api/filesystem/stat/#{path}").success (data) ->
            q.resolve(data)
        .error (err) ->
            q.reject(err)
        return q.promise

    @chmod = (path, mode) ->
        q = $q.defer()
        $http.post("/api/filesystem/chmod/#{path}", mode: mode).success (data) ->
            q.resolve(data)
        .error (err) ->
            q.reject(err)
        return q.promise

    @createFile = (path, mode) ->
        q = $q.defer()
        $http.post("/api/filesystem/create-file/#{path}", mode: mode).success (data) ->
            q.resolve(data)
        .error (err) ->
            q.reject(err)
        return q.promise

    @createDirectory = (path, mode) ->
        q = $q.defer()
        $http.post("/api/filesystem/create-directory/#{path}", mode: mode).success (data) ->
            q.resolve(data)
        .error (err) ->
            q.reject(err)
        return q.promise

    @downloadBlob = (content, mime, name) ->
        setTimeout () ->
            blob = new Blob([content], {type: mime})
            elem = window.document.createElement('a')
            elem.href = URL.createObjectURL(blob)
            elem.download = name
            document.body.appendChild(elem)
            elem.click()
            document.body.removeChild(elem)

    return this

angular.module('ajenti.filesystem').service('filesystem', function($rootScope, $http, $q) {
    this.mountpoints = () =>
      $http.get("/api/filesystem/mountpoints").then(response => response.data)

    this.read = (path, encoding) =>
      $http.get(`/api/filesystem/read/${path}?encoding=${encoding || 'utf-8'}`).then(response => response.data)

    this.write = (path, content, encoding) =>
      $http.post(`/api/filesystem/write/${path}?encoding=${encoding || 'utf-8'}`, content).then(response => response.data)

    this.list = (path) =>
      $http.get(`/api/filesystem/list/${path}`).then(response => response.data)

    this.stat = (path) =>
      $http.get(`/api/filesystem/stat/${path}`).then(response => response.data)

    this.chmod = (path, mode) =>
      $http.post(`/api/filesystem/chmod/${path}`, {mode}).then(response => response.data)

    this.createFile = (path, mode) =>
      $http.post(`/api/filesystem/create-file/${path}`, {mode}).then(response => response.data)

    this.createDirectory = (path, mode) =>
      $http.post(`/api/filesystem/create-directory/${path}`, {mode}).then(response => response.data)

    this.downloadBlob = (content, mime, name) =>
        setTimeout(() => {
            let blob = new Blob([content], {type: mime});
            let elem = window.document.createElement('a');
            elem.href = URL.createObjectURL(blob);
            elem.download = name;
            document.body.appendChild(elem);
            elem.click();
            document.body.removeChild(elem);
        })

    this.startFlowUpload = ($flow, path) => {
        q = $q.defer()
        $flow.on('fileProgress', (file, chunk) => {
            $rootScope.$apply(() => {
                q.notify($flow.files[0].progress())
            })
        })
        $flow.on('complete', async () => {
            $flow.off('complete')
            $flow.off('fileProgress')
            let response = await $http.post(`/api/filesystem/finish-upload`, {
                id: $flow.files[0].uniqueIdentifier, path, name: $flow.files[0].name
            })
            $rootScope.$apply(() => {
                q.resolve(response.data)
            })
            $flow.cancel()
        })

        $flow.upload()
        return q.promise
    }

    return this;
});

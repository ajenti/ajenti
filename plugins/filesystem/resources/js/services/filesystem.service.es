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

    this.createFile = (path) =>
      $http.post(`/api/filesystem/create-file/${path}`)

    this.createDirectory = (path) =>
      $http.post(`/api/filesystem/create-directory/${path}`)

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
                // $flow.files may contain more than one file
                var uploadProgress = []
                for (var file of $flow.files) {
                    uploadProgress.push({
                        id: file.uniqueIdentifier, name: file.name, progress: Math.floor(100*file.progress())
                    })
                }
                q.notify(uploadProgress)
            })
        })
        $flow.on('complete', async () => {
            $flow.off('complete')
            $flow.off('fileProgress')
            let filesToFinish = []
            for (var file of $flow.files) {
                filesToFinish.push({
                    id: file.uniqueIdentifier, path, name: file.name
                })
            }
            let response = await $http.post(`/api/filesystem/finish-upload`, filesToFinish)
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

let __ngBootstrap = (exclude) => {
    exclude = exclude || []
    let modules = []
    for (let pluginName in window.__ngModules) {
        if (exclude.contains(pluginName))
            continue
        modules = modules.concat(window.__ngModules[pluginName])
    }

    let id = 'app__' + Date.now()
    angular.module(id, modules)
    angular.bootstrap(document, [id])
}

let __ngShowBootstrapError = () => {
    $('.global-bootstrap-error').show()
    console.error('Angular bootstrap has failed')
    console.warn('Consider sending the following error to https://github.com/ajenti/ajenti/issues/new')
}

let __ngShowBootstrapRecovered = (plugin) => {
    $('.global-bootstrap-recovered').removeClass('hidden')
    $('.global-bootstrap-recovered .plugin-name').text(plugin)
    $('.global-bootstrap-recovered .btn-close').click(() => {
        $('.global-bootstrap-recovered').remove()
    })
}


window.ajentiBootstrap = () => {
    try {
        __ngBootstrap()
    } catch(e) {
        console.warn('Well, this is awkward')
        console.group('Angular bootstrap has failed:')
        console.error(e)

        for (let pluginName in window.__ngModules) {
            try {
                __ngBootstrap([pluginName])
                console.log(`Worked with ${pluginName} disabled!`)
                console.groupEnd()
                __ngShowBootstrapRecovered(pluginName)
                return
            } catch (e) {
                console.warn(`Still failing with ${pluginName} disabled:`, e)
            }
        }

        console.groupEnd()
        window.__ngShowBootstrapError()
        throw e
    }
}

angular.module('core').constant('urlPrefix', '/urlPrefix')
angular.module('core').constant('ajentiPlugins', [])
angular.module('core').constant('ajentiVersion', 'testenv')

for m in window.__ngModules
    beforeEach module(m)

beforeEach () ->
    inject ($httpBackend, urlPrefix)->
        $httpBackend.oldWhen = $httpBackend.when
        $httpBackend.when = (method, url) ->
            return $httpBackend.oldWhen(method, urlPrefix + url)

        for m in ['expectGET', 'expectPOST']
            $httpBackend['old' + m] = $httpBackend[m]
            $httpBackend[m] = (url) ->
                return $httpBackend['old' + m](urlPrefix + url)

require 'coffee-script'

specs = [
    'specs/notepad.coffee'
    'specs/filemanager.coffee'
    #'specs/terminal.coffee'
]

exports.config =
    seleniumAddress: 'http://localhost:4444/wd/hub'
    specs: specs
    framework: 'jasmine'
    jasmineNodeOpts:
        silent: true
    onPrepare: () ->
        global.By = `global.by`

        global.takeScreenshot = (f) ->
            browser.takeScreenshot().then (data) ->
                fs.writeFile("#{f}.png", data, 'binary')

        global.bindElements = (page, elements) ->
            for b in elements
                page[b] = $("*[test-bind=#{b}]")

        beforeEach () ->
            browser.manage().window().maximize()
            browser.manage().deleteAllCookies()

        global.expectVisible = (e) ->
            expect(e.isDisplayed()).toBeTruthy()

        global.expectNotVisible = (e) ->
            expect(e.isDisplayed()).toBeFalsy()

        global.expectGone = (e) ->
            expect(e.isPresent()).toBeFalsy()

        global.it = () ->
            return jasmine.getEnv().it.apply(jasmine.getEnv(), arguments)

        theOriginalFail = jasmine.Spec.prototype.fail
        jasmine.Spec.prototype.fail = (e) ->
            theOriginalFail.apply(this, arguments);
            console.error(jasmine.util.formatException(e))
            takeScreenshot("fail-#{jasmine.getEnv().currentSpec.name}")

        SpecReporter = require 'jasmine-spec-reporter'
        jasmine.getEnv().addReporter(new SpecReporter(displayStacktrace: true))

    capabilities:
        browserName: 'chrome'
        shardTestFiles: true
        maxInstances: specs.length

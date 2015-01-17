fs = require 'fs'
execSync = require 'exec-sync'

testDir = '/tmp/testenv'
testContent = 'test content!'
testContent2 = 'updated content'

beforeEach () ->
    browser.manage().window().maximize()
    browser.manage().deleteAllCookies()
    execSync("mkdir -p '#{testDir}'")
    fs.writeFileSync("#{testDir}/test.txt", testContent, 'utf8')

afterEach () ->
    execSync("rm -rf '#{testDir}'")

afterEach () ->
    passed = jasmine.getEnv().currentSpec.results().passed()
    if not passed
        jasmine.getEnv().specFilter = (spec) -> 
            return false;


describe 'notepad plugin', () ->
    notepadLoadFile = (path) ->
        # open dialog
        element(By.linkText('OPEN')).click()
        expect(element(By.css('file-dialog[mode=open]')).isDisplayed()).toBeTruthy()
        for token in path.split('/')
            if token
                element(By.partialLinkText(token)).click()
        expect(element(By.css('file-dialog[mode=open]')).isDisplayed()).toBeFalsy()

    it 'should load files', () ->
        browser.get('/view/notepad')
        notepadLoadFile(testDir + '/test.txt')
        expect(browser.getCurrentUrl()).toContain("/view/notepad/#{testDir}/test.txt")
        expect(element(By.css('.ace_line')).getText()).toContain(testContent)

    it 'should load files from URL', () ->
        browser.get("/view/notepad/#{testDir}/test.txt")
        expect(element(By.css('.ace_line')).getText()).toContain(testContent)

    it 'should save files', () ->
        browser.get("/view/notepad/#{testDir}/test.txt")
        # Erase content
        expect(element(By.css('.ace_line')).getText()).toContain(testContent)
        for i in [0...20]
            element(By.css('.ace_text-input')).sendKeys(protractor.Key.BACK_SPACE)
        # Input new content
        element(By.css('.ace_text-input')).sendKeys(testContent2)
        expect(element(By.css('.ace_line')).getText()).toContain(testContent2)
        # Save
        element(By.linkText('SAVE')).click()
        # Verify
        browser.get("/view/notepad/#{testDir}/test.txt")
        expect(element(By.css('.ace_line')).getText()).toContain(testContent2)


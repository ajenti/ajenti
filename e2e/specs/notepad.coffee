fs = require 'fs'
execSync = require 'exec-sync'

testDir = '/tmp/testenv-notepad'
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


class NotepadPage
    constructor: () ->
        @openDialog = element By.css 'file-dialog[mode=open]'
        @saveDialog = element By.css 'file-dialog[mode=save]'
        @saveDialogInput = @saveDialog.element By.css 'input[type=text]'
        @newButton = element By.linkText 'NEW'
        @openButton = element By.linkText 'OPEN'
        @saveButton = element By.linkText 'SAVE'
        @saveAsButton = element By.linkText 'SAVE AS...'
        @editor = element By.css '.ace_line'
        @editorInput = element By.css '.ace_text-input'

    get: (url) ->
        url ?= ''
        browser.get "/view/notepad/#{url}"

    doLoadFile: (path) ->
        @openButton.click()
        expect(@openDialog.isDisplayed()).toBeTruthy()
        for token in path.split('/')
            if token
                @openDialog.element(By.partialLinkText(token)).click()
        expect(@openDialog.isDisplayed()).toBeFalsy()

    doSaveFileAs: (path, name) ->
        @saveAsButton.click()
        expect(@saveDialog.isDisplayed()).toBeTruthy()
        for token in path.split('/')
            if token
                @saveDialog.element(By.partialLinkText(token)).click()
        @saveDialogInput.clear()
        @saveDialogInput.sendKeys(name)
        @saveDialog.element(By.linkText('SAVE')).click()
        expect(@saveDialog.isDisplayed()).toBeFalsy()


describe 'notepad plugin', () ->
    it 'should create new files', () ->
        page = new NotepadPage()
        page.get("#{testDir}/test.txt")
        page.newButton.click()
        browser.switchTo().alert().accept()
        expect(page.editor.getText()).not.toContain(testContent)

    it 'should load files', () ->
        page = new NotepadPage()
        page.get()
        page.doLoadFile(testDir + '/test.txt')
        expect(browser.getCurrentUrl()).toContain("#{testDir}/test.txt")
        expect(page.editor.getText()).toContain(testContent)

    it 'should load files from URL', () ->
        page = new NotepadPage()
        page.get("#{testDir}/test.txt")
        expect(page.editor.getText()).toContain(testContent)

    it 'should save files', () ->
        page = new NotepadPage()
        page.get("#{testDir}/test.txt")
        # Erase content
        expect(page.editor.getText()).toContain(testContent)
        for i in [0...20]
            page.editorInput.sendKeys(protractor.Key.BACK_SPACE)
        # Input new content
        page.editorInput.sendKeys(testContent2)
        expect(page.editor.getText()).toContain(testContent2)
        # Save
        page.saveButton.click()
        # Verify
        page.get("#{testDir}/test.txt")
        expect(page.editor.getText()).toContain(testContent2)

    it 'should save files as...', () ->
        page = new NotepadPage()
        page.get("#{testDir}/test.txt")
        page.doSaveFileAs(testDir, 'test2.txt')
        expect(browser.getCurrentUrl()).toContain('test2.txt')
        page.get("#{testDir}/test2.txt")
        expect(page.editor.getText()).toContain(testContent)

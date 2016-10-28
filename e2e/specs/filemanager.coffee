fs = require 'fs'
execSync = require('child_process').execSync

testDir = '/tmp/testenv-filemanager'

beforeEach () ->
    execSync("mkdir -p '#{testDir}'")
    execSync("mkdir -p '#{testDir}/dir'")
    fs.writeFileSync("#{testDir}/1.txt", '', 'utf8')
    fs.writeFileSync("#{testDir}/2.txt", '', 'utf8')

afterEach () ->
    execSync("rm -rf '#{testDir}'")


class FileManagerPage
    constructor: () ->
        bindElements this, [
            'fileList',
            'up',
            'showClipboardButton',
            'newFileButton',
            'newDirectoryButton',
            'uploadButton',
            'pasteButton',
            'selectionToolbar',
            'cutButton',
            'copyButton',
            'deleteButton',
            'newFileDialog',
            'newFileDialogInput',
            'newFileDialogOk',
            'newFileDialogCancel',
            'newDirectoryDialog',
            'newDirectoryDialogInput',
            'newDirectoryDialogOk',
            'newDirectoryDialogCancel',
            'uploadDialog',
            'uploadDialogUploadPanel',
            'uploadDialogSelectionPanel',
            'uploadDialogSelectButton',
            'uploadDialogCancel',
            'clipboardDialog',
            'clipboardDialogList',
            'clipboardDialogClear',
            'clipboardDialogCancel',
        ]

    get: (url) ->
        url ?= ''
        browser.get "/view/filemanager/#{url}"

    listCheckbox: (name) ->
        return @fileList.$("div[test-bind-item='#{name}'] span[checkbox]")

    listItem: (name) ->
        return @fileList.$("div[test-bind-item='#{name}'] .list-group-main")

    clipboardListItem: (name) ->
        return @clipboardDialogList.$("div[test-bind-item='#{name}']")


describe 'filemanager plugin', () ->
    page = new FileManagerPage()

    it 'should load dirs by url', () ->
        page.get(testDir)
        expectVisible(page.listItem('dir'))

    it 'should navigate', () ->
        page.get(testDir)
        page.listItem('dir').click()
        expect(browser.getCurrentUrl()).toContain("#{testDir}/dir")
        page.up.click()
        expect(browser.getCurrentUrl()).toContain("#{testDir}")
        expectVisible(page.listItem('dir'))

    it 'should show selection toolbar', () ->
        page.get(testDir)
        page.listCheckbox('1.txt').click()
        expectVisible(page.selectionToolbar)

    it 'should have working clipboard', () ->
        page.get(testDir)

        page.listCheckbox('1.txt').click()
        page.cutButton.click()
        page.listCheckbox('2.txt').click()
        page.copyButton.click()

        page.showClipboardButton.click()
        expectVisible(page.clipboardDialog)
        expectVisible(page.clipboardListItem('1.txt'))
        expectVisible(page.clipboardListItem('2.txt'))

        page.clipboardDialogCancel.click()
        expectNotVisible(page.clipboardDialog)

        page.showClipboardButton.click()
        page.clipboardListItem('1.txt').$('a').click()
        expectGone(page.clipboardListItem('1.txt'))

        page.clipboardDialogClear.click()
        expectNotVisible(page.pasteButton)
        expectNotVisible(page.showClipboardButton)

    it 'should create files', () ->
        page.get(testDir)
        page.newFileButton.click()
        expectVisible(page.newFileDialog)

        page.newFileDialogCancel.click()
        expectNotVisible(page.newFileDialog)

        page.newFileButton.click()
        page.newFileDialogInput.sendKeys('new.txt')
        page.newFileDialogOk.click()
        expectNotVisible(page.newFileDialog)
        expectVisible(page.listItem('new.txt'))

    it 'should create dirs', () ->
        page.get(testDir)
        page.newDirectoryButton.click()
        expectVisible(page.newDirectoryDialog)

        page.newDirectoryDialogCancel.click()
        expectNotVisible(page.newDirectoryDialog)

        page.newDirectoryButton.click()
        page.newDirectoryDialogInput.sendKeys('newdir')
        page.newDirectoryDialogOk.click()
        expectNotVisible(page.newDirectoryDialog)
        expectVisible(page.listItem('newdir'))

    it 'should move files', () ->
        page.get(testDir)
        page.listCheckbox('1.txt').click()
        page.cutButton.click()
        page.listItem('dir').click()
        page.pasteButton.click()
        browser.sleep(2000)
        expectVisible(page.listItem('1.txt'))

        page.get(testDir)
        expectGone(page.listItem('1.txt'))

    it 'should copy files', () ->
        page.get(testDir)
        page.listCheckbox('1.txt').click()
        page.copyButton.click()
        page.listItem('dir').click()
        page.pasteButton.click()
        browser.sleep(2000)
        expectVisible(page.listItem('1.txt'))

        page.get(testDir)
        expectVisible(page.listItem('1.txt'))

    it 'should delete files', () ->
        page.get(testDir)
        page.listCheckbox('1.txt').click()
        page.deleteButton.click()
        element(By.css('messagebox-container .positive')).click()
        browser.sleep(1000)
        expectGone(page.listItem('1.txt'))

    it 'should upload files', () ->
        page.get("#{testDir}/dir")

        page.uploadButton.click()
        expectVisible(page.uploadDialog)
        page.uploadDialogCancel.click()
        expectNotVisible(page.uploadDialog)

        page.uploadButton.click()
        page.uploadDialog.$('input[type=file]').sendKeys("#{testDir}/1.txt")
        browser.sleep(3000)
        expectNotVisible(page.uploadDialog)
        expectVisible(page.listItem('1.txt'))

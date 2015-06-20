class TerminalPage
    constructor: () ->
        bindElements this, [
            'terminalList',
            'newTerminalButton',
            'newTerminalButton2',
        ]
        @terminal = element By.css 'canvas'
        @content = element By.css '.ace_line'

    get: (url) ->
        url ?= ''
        browser.get "/view/terminal/#{url}"


describe 'terminal plugin', () ->
    page = new TerminalPage()

    it 'should show new button', () ->
        page.get()
        expectVisible(page.newTerminalButton)

    it 'should have working terminals', () ->
        page.get()
        page.newTerminalButton.click()
        expect(browser.getCurrentUrl()).toContain("terminal/")
        #browser.actions().sendKeys("clear; echo TEST\n").perform()
        browser.sleep(1000)
        expect(page.content.getText()).toContain('TEST1')
        #page.content.getText().catch (e) ->
        #    console.log 'E>>', e

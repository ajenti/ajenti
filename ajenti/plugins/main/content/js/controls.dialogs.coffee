class window.Controls.dialog extends window.Control
    createDom: () ->
        """
            <div class="control container dialog #{@s(@properties.style)}">
                <div class="backdrop">
                    <div class="content">
                        <div class="--child-container">
                            <children>
                        </div>
                    </div>
                </div>
            </div>
        """

    setupDom: (dom) ->
        super(dom)
        if @properties.buttons
            @buttons = $("""<div class="buttons"></div>""")
            $(@dom).find('>.backdrop>.content').append(@buttons)
            container = new Controls.hc(@ui)
            container.setupDom()
            @buttons.append container.dom
            for button in @properties.buttons
                do (button) =>
                    b = new Controls.button(@ui, {
                            text: button.text
                            icon: button.icon
                            style: 'normal'
                        })
                    b.setupDom()
                    b.on_click = () =>
                        @event('button', button: button.id)
                    container.append(b)

        
class window.Controls.inputdialog extends Controls.dialog
    createDom: () ->
        @input = new Controls.textbox(@ui, { value: @properties.value }, [])
        body = new Controls.pad(@ui, {}, [
            new Controls.hc(@ui, {}, [
                new Controls.label(@ui, { text: @properties.text }, []),
                @input
            ])
        ])
        #@children.push body
        super()

    setupDom: (dom) ->
        @properties.buttons = [
            {
                text: 'OK'
                id: 'ok'
            },
            {
                text: 'Cancel'
                id: 'cancel'
            },
        ]
        super(dom)

    detectUpdates: () ->
        r = {}
        value = @input.getValue()
        if value != @properties.value
            r.value = value
        @properties.value = value
        return r


class window.Controls.openfiledialog extends Controls.dialog
    setupDom: (dom) ->
        @properties.buttons = [
            {
                text: 'Cancel'
                id: 'cancel'
            },
        ]
        super(dom)



class window.Controls.opendirdialog extends Controls.dialog
    setupDom: (dom) ->
        @properties.buttons = [
            {
                text: 'Select'
                id: 'select'
            },
            {
                text: 'Cancel'
                id: 'cancel'
            },
        ]
        super(dom)


class window.Controls.savefiledialog extends Controls.dialog
    setupDom: (dom) ->
        @properties.buttons = [
            {
                text: 'Cancel'
                id: 'cancel'
            },
            {
                text: 'Save'
                id: 'ok'
            },
        ]
        super(dom)
        @input = $(@dom).find('input')

    on_button: (params) =>
        if params.button != 'ok'
            return true
        if @input.val().length > 0
            @event('select', path: @properties.path + '/' + @input.val())

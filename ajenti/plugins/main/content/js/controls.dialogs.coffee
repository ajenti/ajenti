class window.Controls.dialog extends window.Control
    createDom: () ->
        @dom = $("""
            <div class="control container dialog">
                <div class="backdrop">
                    <div class="content">
                        <div class="children">
                        </div>
                    </div>
                </div>
            </div>
        """)
        @childContainer = @dom.find('.children')
        if @properties.buttons
            @buttons = $("""<div class="buttons"></div>""")
            @dom.find('.content').append(@buttons)
            container = new Controls.hc(@ui)
            @buttons.append container.dom
            for button in @properties.buttons
                do (button) =>
                    b = new Controls.button(@ui, {
                            text: button.text
                            icon: button.icon
                            style: 'normal'
                        })
                    b.on_click = () =>
                        @event('button', button: button.id)
                    container.append(b)

        
class window.Controls.inputdialog extends Controls.dialog
    createDom: () ->
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
        super()
        @input = new Controls.textbox(@ui, { value: @properties.value }, [])
        @append new Controls.pad(@ui, {}, [
            new Controls.hc(@ui, {}, [
                new Controls.label(@ui, { text: @properties.text }, []),
                @input
            ])
        ])

    detectUpdates: () ->
        r = {}
        value = @input.properties.value
        if value != @properties.value
            r.value = value
        @properties.value = value
        return r


class window.Controls.openfiledialog extends Controls.dialog
    createDom: () ->
        @properties.buttons = [
            {
                text: 'Cancel'
                id: 'cancel'
            },
        ]
        super()

        @container = new Controls.list(@ui) 
        @append new Controls.pad(@ui, {}, [
                    new Controls.box(@ui, { width: 'auto', height: 300, scroll: true }, [@container])
                ])

        for dir in @properties._dirs
            do (dir) =>
                item = new Controls.hc(@ui, {}, [
                    new Controls.icon(@ui, { icon: 'folder-open' }),
                    new Controls.label(@ui, { text: dir })
                ])
                $(item.dom).click () =>
                    @event('item-click', item: dir)
                @container.append new Controls.listitem(@ui, {}, [item])
        for file in @properties._files
            do (file) =>
                item = new Controls.hc(@ui, {}, [
                    new Controls.icon(@ui, { icon: 'file' }),
                    new Controls.label(@ui, { text: file })
                ])
                $(item.dom).click () =>
                    @event('item-click', item: file)
                @container.append new Controls.listitem(@ui, {}, [item])


class window.Controls.opendirdialog extends Controls.dialog
    createDom: () ->
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
        super()

        @container = new Controls.list(@ui) 
        @append new Controls.pad(@ui, {}, [
                    new Controls.box(@ui, { width: 'auto', height: 300, scroll: true }, [@container])
                ])

        for dir in @properties._dirs
            do (dir) =>
                item = new Controls.hc(@ui, {}, [
                    new Controls.icon(@ui, { icon: 'folder-open' }),
                    new Controls.label(@ui, { text: dir })
                ])
                $(item.dom).click () =>
                    @event('item-click', item: dir)
                @container.append new Controls.listitem(@ui, {}, [item])


class window.Controls.savefiledialog extends Controls.dialog
    createDom: () ->
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
        super()

        @input = new Controls.textbox(@ui, { value: '' })
        @container = new Controls.list(@ui) 
        @append new Controls.pad(@ui, {}, [
                    new Controls.vc(@ui, {}, [
                        new Controls.box(@ui, { width: 'auto', height: 300, scroll: true}, [@container]),
                        new Controls.hc(@ui, {}, [
                            new Controls.label(@ui, {text: 'Name: '}),
                            @input
                        ])
                    ])
                ])

        for dir in @properties._dirs
            do (dir) =>
                item = new Controls.hc(@ui, {}, [
                    new Controls.icon(@ui, { icon: 'folder-open' }),
                    new Controls.label(@ui, { text: dir })
                ])
                $(item.dom).click () =>
                    @event('item-click', item: dir)
                @container.append new Controls.listitem(@ui, {}, [item])

    on_button: (params) =>
        if params.button != 'ok'
            return true
        if @input.properties.value.length > 0
            @event('select', path: @properties.path + '/' + @input.properties.value)

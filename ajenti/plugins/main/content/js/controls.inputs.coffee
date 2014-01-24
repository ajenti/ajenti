class window.Controls.textbox extends window.Control
    createDom: () ->
        """
            <input class="control textbox #{@s(@properties.style)}" 
                    #{if @properties.readonly then 'readonly' else ''}
                    type="text" />
        """

    setupDom: (dom) ->
        super(dom)
        @input = @dom
        @input.value = @properties.value
        @input.addEventListener 'change', () => 
            @markChanged()
        , false
        return this

    getValue: () ->
        $(@input).val()
        
    detectUpdates: () ->
        r = {}
        value = @getValue()
        oldvalue = @properties.value || ""
        if @properties.type == 'integer'
            value = parseInt(value)
        if value != oldvalue
            r.value = value
        @properties.value = value
        return r


class window.Controls.passwordbox extends window.Controls.textbox
    createDom: () ->
        """
            <input class="control textbox #{@properties.style}" 
                    type="password" />
        """

    setupDom: (dom) ->
        super(dom)
        @input = $(@dom)
        @input.val(@properties.value)
        @input.change () => @markChanged()
        return this


class window.Controls.editable extends window.Control
    createDom: () ->
        icon = _make_icon(@properties.icon)
        """
            <div class="control editable">
                <div class="control label">#{icon} <span>#{@s(@properties.placeholder ? @properties.value)}</span></div>
                <input class="control textbox #{@properties.style}" type="text" />
            </div>
        """

    setupDom: (dom) ->
        super(dom)
        @label = $(@dom).find('.label')
        @input = $(@dom).find('input')
        @input.val(@properties.value or '')
        @input.hide()
        @input.change () => @markChanged()
        @editmode = false
        @label.click @goEditMode
        @input.blur @goViewMode
        @input.keyup (e) =>
            if e.which == 13
                @goViewMode()
            @cancel(e)
        return this

    goViewMode: () =>
        @editmode = false
        @label.find('>span').html(@properties.placeholder ? @input.val())
        @input.hide()
        @label.show()

    goEditMode: (e) =>
        @editmode = true
        @label.hide()
        @input.show()
        @input.focus()
        e.stopPropagation()
        e.preventDefault()

    detectUpdates: () ->
        r = {}
        if @editmode
            goViewMode()
        value = @input.val()
        if @properties.type == 'integer'
            value = parseInt(value)
        if value != @properties.value
            r.value = value
        return r


class window.Controls.checkbox extends window.Control
    createDom: () ->
        """
            <div class="control checkbox">
                <input 
                    id="#{@properties.uid}"
                    type="checkbox" 
                    #{if @properties.value then 'checked="checked"' else ''} 
                />
                <label for="#{@properties.uid}">
                    <div class="tick">
                        <i class="icon-ok"></i>
                    </div>
                </label>
                <div class="control label">#{@s(@properties.text)}</div>
            </div>
        """

    setupDom: (dom) ->
        super(dom)
        @input = $(@dom).find('input')
        @input.change () => @markChanged()
        return this

    detectUpdates: () ->
        r = {}
        checked = @input.is(':checked')
        if checked != @properties.value
            r.value = checked
        @properties.value = checked
        return r


class window.Controls.dropdown extends window.Control
    createDom: () ->
        """
            <div><select class="control dropdown"></select></div>
        """

    setupDom: (dom) ->
        super(dom)
        @input = $(@dom).find('select')
        @data = []
        for i in [0...@properties.labels.length]
            do (i) =>
                @input.append("""<option value="#{i}" #{if i == @properties.index then 'selected' else ''}>#{@s(@properties.labels[i])}</option>""")

        @input.select2()
        @input.change () => @markChanged()
        
        if @properties.server
            @input.change (e) =>
                @event('change', {})
                @cancel(e)
        return this

    detectUpdates: () ->
        r = {}
        index = parseInt(@input.val())
        if index != @properties.index
            r.index = index
        @properties.index = index
        return r


class window.Controls.combobox extends window.Control
    createDom: () ->
        """
            <input class="control combobox" type="text" value="#{@properties.value}" />
        """

    setupDom: (dom) ->
        super(dom)        
        @input = $(@dom)
        @input.change () => @markChanged()
        @data = []
        for i in [0...@properties.labels.length]
            do (i) =>
                @data.push {label: @properties.labels[i], value: @properties.values[i]}

        if @properties.separator != null
            @input.autocomplete {
                source: (request, response) =>
                    vals = @getVals()
                    response($.ui.autocomplete.filter(@data, vals.pop()))
                focus: () =>
                    return false
                select: (event, ui) =>
                    vals = @getVals()
                    vals.pop()
                    vals.push ui.item.value
                    @input.val(vals.join(@properties.separator))
                    return false
                minLength: 0
            }
        else
            @input.autocomplete source: @data, minLength: 0
        @input.click () =>
            @input.autocomplete 'search', ''
        return this

    getVals: () ->
        return @input.val().split(@properties.separator)

    detectUpdates: () ->
        r = {}
        value = @input.val()
        if @properties.type == 'integer'
            value = parseInt(value)
        if value != @properties.value
            r.value = value
        @properties.value = value
        return r



class window.Controls.fileupload extends window.Control
    createDom: () ->
        """
            <div class="control fileupload">
                <input type="file" />
                
                <div class="full-overlay">
                    <div class="content">
                        <div class="inner">
                            <h1>Upload</h1>
                            <div class="pb"></div>
                        </div>
                    </div>
                </div>  
            </div>
        """

    setupDom: (dom) ->
        super(dom)        
        @progress = new window.Controls.progressbar(@ui, {width: 750}, [])
        @progress.setupDom()
        $(@dom).find('.pb').append($(@progress.dom))
        @input = $(@dom).find('input')[0]
        @input.addEventListener 'change', (e) =>
            file = @input.files[0]
            xhr = new XMLHttpRequest()
            xhr.file = file
            
            if xhr.upload
                xhr.upload.onprogress = (e) =>
                    done = e.position || e.loaded
                    total = e.totalSize || e.total
                    progress = 1.0 * done / total
                    @progress.setProgress(progress)

            d = new FormData()
            d.append('file', file)

            xhr.open('post', @properties.target, true)
            xhr.send(d)
            $(@dom).find('.full-overlay').show()
        , false
        $(@dom).find('.full-overlay').hide()


class window.Controls.paging extends window.Control
    createDom: () ->
        """
            <div class="control paging">
                <div class="control label">Page:&nbsp;</div>
                <a class="prev control button style-mini"><i class="icon-arrow-left"></i></a>
                <select></select>
                <a class="next control button style-mini"><i class="icon-arrow-right"></i></a>
            </div>
        """

    setupDom: (dom) ->
        super(dom)
        @select = $(@dom).find('select')
        for i in [0...@properties.length]
            @select.append($$("""
                <option value="#{i+1}">#{i+1}</option>
            """))
        @select.val(@properties.active + 1)
        @select.select2(width: '80px')
        @prev = $(@dom).find('.prev')
        @next = $(@dom).find('.next')

        if @properties.active == 0
            @prev.hide()
        if @properties.active == @properties.length - 1
            @next.hide()
        if !@properties.length
            $(@dom).hide()

        @prev.click () =>
            @set(@properties.active - 1)
        @next.click () =>
            @set(@properties.active + 1)
        @select.change () =>
            idx = parseInt(@select.val()) - 1
            console.log idx, @properties.active
            if idx != @properties.active
                @set(idx)
        return this

    set: (page) ->
        @event('switch', page: page)


class window.Controls.pathbox extends window.Control
    createDom: () ->
        """
            <div class="control container pathbox --child-container">
                <children>
            </div>
        """

    setupDom: (dom) ->
        super(dom)
        @textbox = new Controls.textbox(@ui, value: @properties.value).setupDom()
        @button = new Controls.button(
            @ui, 
            style: 'mini'
            icon: if @properties.directory then 'folder-close' else 'file'
            text: ''
        ).setupDom()
        @append(@textbox)
        @append(@button)

        @button.on_click = () =>
            @event('start', {})
        return this

    detectUpdates: () ->
        return @textbox.detectUpdates()

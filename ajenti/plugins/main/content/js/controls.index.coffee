class window.Controls.main__page extends window.Control
    createDom: () ->
        @dom = $("""
            <div class="control container main-page"> 
                <div class="content-wr">
                    <div class="content">
                        <div class="--child-container"></div>
                    </div>
                </div>
            </div>
        """)
        @childContainer = @dom.find('.--child-container')



class window.Controls.main__sections_tab extends window.Control
    createDom: () ->
        @dom = $$("""
            <a href="#" class="tab #{if @properties.active then 'active' else ''}">
                <i class="loader pull-right hide-when-loaded icon icon-spinner icon-spin"></i>
                <i class="icon-#{@properties.icon}"></i>&nbsp;#{@properties.title}
            </a>
        """)


class window.Controls.main__sections_category extends window.Control
    createDom: () ->
        @dom = $("""
            <div class="control container main-sections-category"> 
                <div>#{@properties.name}</div>
                <div class="content">
                    <div class="--child-container"></div>
                </div>
            </div>
        """)
        @childContainer = @dom.find('.--child-container')


class window.Controls.main__sections_root extends window.Control
    createDom: () ->
        @dom = $("""
            <div class="control container main-sections-root">
                <div class="sidebar">
                    <div class="--tabs-container"></div>
                </div>
                <div class="main">
                    <div class="--child-container"></div>
                    <div class="no-sections">
                        <div>
                            <div class="control label bold">No plugins are allowed for this user</div>
                        </div>
                        <div>
                            <div class="control label">
                                Please ask your administrator to go to Configuration plugin and give you permissions to access some plugins.
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        """)
        @tabsContainer = @dom.find('.--tabs-container')
        @childContainer = @dom.find('.--child-container')
        @categories = {}

        if not @properties.is_empty
            @dom.find('.no-sections').hide()

    append: (child) ->
        if not @categories[child.properties.category]
            cat = new Controls.main__sections_category(@ui, { name: child.properties.category })
            @categories[child.properties.category] = cat
            @tabsContainer.append(cat.dom)

        tab = new Controls.main__sections_tab(@ui, $.extend(child.properties, { visible: true }))
        $(tab.dom).click (e) =>
            $(tab.dom).find('.loader').show()
            Feedback.emit('Section activated', Class: child.properties.clsname, Name: child.properties.title)
            @event('switch', uid:child.uid)
            e.preventDefault()

        @categories[child.properties.category].append(tab)
        super(child)


class window.Controls.main__section extends window.Control
    createDom: () ->
        @dom = $("""
            <div class="control container section #{if @properties.active then 'active' else ''} #{if @properties.plain then 'plain' else 'normal'}"">
                <div class="--child-container"></div>
            </div>
        """)
        @childContainer = @dom.find('.--child-container')


class window.Controls.body extends window.Control
    createDom: () ->
        @dom = $$("""
            <div class="control container section-body">
            </div>
        """)
        @childContainer = @dom

class window.Controls.main__page extends window.Control
    createDom: () ->
        """
            <div class="control container main-page"> 
                <div class="content-wr">
                    <div class="content">
                        <children>
                    </div>
                </div>
                <footer>
                    <div class="container">
                        <div class="item">
                            <a class="logo" target="_blank" href="http://ajenti.org">ajenti</a>
                        </div>
                        <div class="item">
                            <a href="https://github.com/Eugeny/ajenti/releases" target="_blank" id="version-number">
                                v
                            </a>
                        </div>
                        <div class="item">
                            <a href="https://github.com/Eugeny/ajenti/issues/new" target="_blank">
                                Report a bug
                            </a>
                        </div>
                        <div class="item">
                            <a href="http://support.ajenti.org/" target="_blank">
                                Help &amp; support
                            </a>
                        </div>
                        <div class="item">
                            <a href="https://github.com/Eugeny/ajenti/" target="_blank">
                                Code
                            </a>
                        </div>
                        <div class="item">
                            <a href="http://docs.ajenti.org/en/latest/" target="_blank">
                                Developer docs
                            </a>
                        </div>
                        <div class="item">
                            <a href="/licensing">
                                Licensing
                            </a>
                        </div>
                    </div>
                </footer>
            </div>
        """


class window.Controls.main__sections_tab extends window.Control
    createDom: () ->
        """
            <a href="#" class="tab #{@s(if @properties.active then 'active' else '')}">
                <i class="loader pull-right hide-when-loaded icon icon-spinner icon-spin"></i>
                <i class="icon-#{@s(@properties.icon)}"></i>&nbsp;#{@s(@properties.title)}
            </a>
        """


class window.Controls.main__sections_category extends window.Control
    createDom: () ->
        """
            <div class="control container main-sections-category"> 
                <div>#{@s(@properties.name)}</div>
                <div class="content">
                    <div class="__child-container">
                        <children>
                    </div>
                </div>
            </div>
        """


class window.Controls.main__sections_root extends window.Control
    createDom: () ->
        @requiresAllChildren = true
        """
            <div class="control container main-sections-root">
                <div class="sidebar">
                    <div class="tabs-container"></div>
                </div>
                <div class="main">
                    <div class="child-container">
                        <children>
                    </div>
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
        """

    setupDom: (dom) ->
        super(dom)
        @tabsContainer = $(@dom).find('.tabs-container')
        @categories = {}

        setTimeout () =>
            @restoreScroll()
        , 1

        resizeSidebar = () => 
            setTimeout () =>
                h = ($(window).height() - 80) + 'px'
                $(@dom.children[0].children[0]).css(height: h)
            , 1

        $(document).ready resizeSidebar
        $(window).resize resizeSidebar

        if not @properties.is_empty
            $(@dom).find('.no-sections').remove()

        for child in @children
            do (child) =>
                if not @categories[child.properties.category]
                    cat = new Controls.main__sections_category(@ui, { name: child.properties.category })
                    cat.setupDom()
                    @categories[child.properties.category] = cat
                    @tabsContainer.append(cat.dom)

                tab = new Controls.main__sections_tab(@ui, $.extend(child.properties, { visible: true }))
                tab.setupDom()
                $(tab.dom).click (e) =>
                    $(tab.dom).find('.loader').show()
                    Feedback.emit('Section activated', Class: child.properties.clsname, Name: child.properties.title)
                    @event('switch', uid:child.uid)
                    e.preventDefault()

                if not child.properties.hidden
                    @categories[child.properties.category].append(tab)
    
    saveScroll: () ->
        @constructor._savedScroll = $(@dom.children[0].children[0]).scrollTop()

    restoreScroll: () ->
        $(@dom.children[0].children[0]).scrollTop(@constructor._savedScroll)

    onBroadcast: (msg) ->
        if msg == 'destruct'
            @saveScroll()


class window.Controls.main__section extends window.Control
    createDom: () ->
        """
            <div class="control container section #{if @properties.active then 'active' else ''} normal">
                <children>
            </div>
        """


class window.Controls.body extends window.Control
    createDom: () ->
        """
            <div class="control container section-body">
                <children>
            </div>
        """

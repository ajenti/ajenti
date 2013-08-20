class window.Controls.main__page extends window.Control
    createDom: () ->
        @dom = $("""
            <div class="control container main-page"> 
                <div class="content-wr">
                    <!--div class="feedback">
                        <a class="activate">Leave Feedback</a>
                        <div class="box">
                            <label>Email (optional)</label>
                            <br/>
                            <input class="control textbox" />
                            <br/>
                            <label>Text</label>
                            <br/>
                            <textarea class="control textbox"></textarea>
                            <br/>
                            <a href="#" class="control button style-normal">Submit</a>
                        </div>
                    </div-->

                    <div class="content">
                        <div class="--child-container"></div>
                    </div>
                </div>
            </div>
        """)
        @childContainer = @dom.find('.--child-container')
        @feedback = @dom.find('.feedback')
        @feedback.find('.box').hide()
        
        @feedback.find('.activate').click () =>
            @feedback.find('.box').toggle()

        @feedback.find('.box a').click () =>
            @feedback.find('.box').hide()
            @event('feedback', 
                email: @feedback.find('input').val()
                text: @feedback.find('textarea').val()
            )


class window.Controls.main__sections_tab extends window.Control
    createDom: () ->
        @dom = $("""
            <a href="#" class="tab #{if @properties.active then 'active' else ''}">
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
                </div>
            </div>
        """)
        @tabsContainer = @dom.find('.--tabs-container')
        @childContainer = @dom.find('.--child-container')
        @categories = {}

    append: (child) ->
        if not @categories[child.properties.category]
            cat = new Controls.main__sections_category(@ui, { name: child.properties.category })
            @categories[child.properties.category] = cat
            @tabsContainer.append(cat.dom)

        tab = new Controls.main__sections_tab(@ui, $.extend(child.properties, { visible: true }))
        $(tab.dom).click (e) =>
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
        @dom = $("""
            <div class="control container section-body">
            </div>
        """)
        @childContainer = @dom

class window.Controls.main__page extends window.Control
	createDom: () ->
		@dom = $("""
			<div><div class="--child-container"></div></div>
		""")
		@childContainer = @dom.find('.--child-container')


class window.Controls.main__sections_root extends window.Control
	createDom: () ->
		@dom = $("""
			<div>
				<h1>Sections!</h2>
				<div class="--tabs-container"></div>
				<div class="--child-container"></div>
			</div>
		""")
		@tabsContainer = @dom.find('.--tabs-container')
		@childContainer = @dom.find('.--child-container')

	append: (child) ->
		@tabsContainer.append("""<span>#{child.properties.title}</span>""")
		super(child)


class window.Controls.main__section extends window.Control
	createDom: () ->
		@dom = $("""
			<div class="section">
				<div class="--child-container"></div>
			</div>
		""")
		@childContainer = @dom.find('.--child-container')

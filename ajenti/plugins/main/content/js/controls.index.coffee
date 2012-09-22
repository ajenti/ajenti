class window.Controls.main__page extends window.Control
	createDom: () ->
		@dom = $("""
			<div class="control main-page"> 
				<div class="header">
				</div>
				<div class="content">
					<div class="--child-container"></div>
				</div>
				<div class="footer">
				</div>
			</div>
		""")
		@childContainer = @dom.find('.--child-container')


class window.Controls.main__sections_root extends window.Control
	createDom: () ->
		@dom = $("""
			<div class="control main-sections-root">
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

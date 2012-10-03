class window.Controls.main__page extends window.Control
	createDom: () ->
		@dom = $("""
			<div class="control container main-page"> 
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

	append: (child) ->
		tab = $("""
			<a href="#" class="tab #{if child.properties.active then 'active' else ''}">
				#{child.properties.title}
			</a>
		""")
		tab.click (e) =>
			@event('switch', uid:child.uid)
			e.preventDefault()

		@tabsContainer.append(tab)
		super(child)


class window.Controls.main__section extends window.Control
	createDom: () ->
		@dom = $("""
			<div class="control section container #{if @properties.active then 'active' else ''}">
				<div class="--child-container"></div>
			</div>
		""")
		@childContainer = @dom.find('.--child-container')

class window.Controls.main__page extends window.Control
	createDom: () ->
		@dom = $("""
			<div class="control container main-page"> 
				<div class="header">
					<div class="container">
						<div class="userbox">
							<div class="logout">
								<a href="/logout"><i class="icon-off icon-white"></i></a>
							</div>
							<div class="username">
								#{@properties.username}
							</div>
							<div>
								<i class="icon-user icon-white"></i>
							</div>
						</div>
					</div>
				</div>
				<div class="content-wr">
					<div class="content">
						<div class="--child-container"></div>
					</div>
				</div>
				<div class="footer">
					<div class="container">
						<div class="name">
							Ajenti
							<div class="url"><a href="http://ajenti.org" target="_blank">ajenti.org</a></div>
						</div>

						<div class="link">
							<a href="" target="_blank">Homepage</a>
						</div>

						<div class="link">
							<a href="" target="_blank">Wiki</a>
						</div>

						<div class="link">
							<a href="" target="_blank">Bugtracker</a>
						</div>
					</div>
				</div>
			</div>
		""")
		@childContainer = @dom.find('.--child-container')


class window.Controls.main__sections_tab extends window.Control
	createDom: () ->
		@dom = $("""
			<a href="#" class="tab #{if @properties.active then 'active' else ''}">
				#{@properties.title}
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
		tab.dom.click (e) =>
			@event('switch', uid:child.uid)
			e.preventDefault()

		@categories[child.properties.category].append(tab)
		super(child)


class window.Controls.main__section extends window.Control
	createDom: () ->
		@dom = $("""
			<div class="control section container #{if @properties.active then 'active' else ''}">
				<div class="--child-container"></div>
			</div>
		""")
		@childContainer = @dom.find('.--child-container')

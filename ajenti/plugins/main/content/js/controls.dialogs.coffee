class window.Controls.openfiledialog extends window.Control
	createDom: () ->
		@dom = $("""
			<div class="control dialog openfiledialog"> 
			</div>
		""")
		@container = new Controls.vc(@ui) 
		@dom.append new Controls.box(@ui, { width: 300, height: 300, scroll: true}, [@container]).dom

		for dir in @properties._dirs
			do (dir) =>
				item = new Controls.hc(@ui, null, [
					new Controls.icon(@ui, { icon: 'folder-open' }),
					new Controls.label(@ui, { text: dir })
				])
				item.dom.click () =>
					@event('item-click', item: dir)
				@container.append item
		for file in @properties._files
			do (file) =>
				item = new Controls.hc(@ui, null, [
					new Controls.icon(@ui, { icon: 'file' }),
					new Controls.label(@ui, { text: file })
				])
				item.dom.click () =>
					@event('item-click', item: file)
				@container.append item

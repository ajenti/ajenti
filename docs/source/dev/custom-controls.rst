.. _dev-custom-controls:

Custom UI Controls
******************

You can create any type of a reusable UI control. Remember to take a look at default controls in ``ajenti/plugins/main`` for guidance.

Example
=======

In this example, we'll create a HTML5 slider control.

Code::

    from ajenti.api import plugin
    from ajenti.plugins.main.api import SectionPlugin
    from ajenti.ui import on, p, UIElement


    @plugin
    class Test (SectionPlugin):
        def init(self):
            self.title = 'Controls'
            self.icon = 'smile'
            self.category = 'Demo'
            self.append(self.ui.inflate('test_controls:main'))

        @on('check', 'click')
        def on_show(self):
            self.context.notify('info', 'Value is %i' % self.find('slider').value)


    @p('value', type=int, default=0)
    @plugin
    class Slider (UIElement):
        typeid = 'slider'


Layout::

    <body>
        <pad>
            <vc>
                <formline text="Slider">
                    <slider id="slider" value="0" />
                </formline>
                <formline>
                    <button icon="ok" id="check" text="Get value" />
                </formline>
            </vc>
        </pad>
    </body>

Control class is decorated with :func:`ajenti.ui.p` for each of its properties.
The main client-side logic is implemented through CoffeeScript code (though you can try to get away with pure-JS).

CoffeeScript::

    class window.Controls.slider extends window.Control
        createDom: () ->
            # createDom() must return HTML
            """
                <div>
                    <input type="range" min="0" max="10" />
                </div>
            """

        setupDom: (dom) ->
            # setupDom may attach event handler and perform other DOM manipulations
            # use this.properties hash to populate control with its current state
            super(dom)
            @input = $(@dom).find('input')
            @input.val(@properties.value)

        detectUpdates: () ->
            # detectUpdates() should return a hash containing only changed properties
            # be sure to not report unchanged properties since this will lead to infinite update loops
            r = {}
            value = parseInt(@input.val())
            if value != @properties.value
                r.value = value
            return r
        
.. image:: /_static/dev/control.png

`Download this example </_static/dev/test_controls.tar.gz>`_

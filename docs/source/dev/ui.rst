.. _dev-ui:

Building User Interfaces
************************

Theory
======

The whole Ajenti UI is a DOM tree of :class:`ajenti.ui.UIElement` objects. After each update, the UI tree is serialized into JSON and sent to browser, where HTML DOM is assembled from it with the help of CoffeeScript code.
Unlike conventional web apps, Ajenti is a stateful machine, which means you adopt a simple workflow similar to developing desktop apps, not websites.

Example
=======

Replace the contents of ``main.py`` from the :ref:`Plugins tutorial <dev-plugins>`::

    from ajenti.api import *
    from ajenti.plugins.main.api import SectionPlugin
    from ajenti.ui import on


    @plugin
    class TestPlugin (SectionPlugin):
        def init(self):
            self.title = 'Test'  # those are not class attributes and can be only set in or after init()
            self.icon = 'question'
            self.category = 'Demo'

            """
            UI Inflater searches for the named XML layout and inflates it into
            an UIElement object tree
            """
            self.append(self.ui.inflate('test:main'))

            self.counter = 0
            self.refresh()

        def refresh(self):
            """
            Changing element properties automatically results 
            in an UI updated being issued to client
            """
            self.find('counter-label').text = 'Counter: %i' % self.counter

        @on('increment-button', 'click')
        def on_button(self):
            """
            This method is called every time a child element 
            with ID 'increment-button' fires a 'click' event
            """
            self.counter += 1
            self.refresh()


Add a subdirectory ``layout`` and place a file named ``main.xml`` there::

    <body> <!-- an overall plugin container panel -->
        <pad> <!-- adds whitespace padding -->
            <hc> <!-- horizontal container -->
                <label id="counter-label" />
                <button id="increment-button" text="+1" style="mini" />
            </hc>
        </pad>
    </body>

(refer to the :ref:`List of UI Elements <dev-ui-elements>`).

Now restart Ajenti. The new plugin **Test** will be visible under **Demo** category. Clicking the **+1** button will increase the counter.

.. image:: /_static/dev/ui/example.png

The visible part of plugin is an UIElement, inherited from :class:`ajenti.plugins.main.api.SectionPlugin`.

When you click the button, the 'click' even is fired down the UI tree. The first method to have correctly decorated ``@on`` method will handle the event. Alternatively, you can set event handler on the element itself by adding this code to ``init``::

    self.find('increment-button').on('click', self.on_button)

Continue to :ref:`Bindings <dev-binding>`

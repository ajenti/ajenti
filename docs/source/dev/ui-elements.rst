.. _dev-ui-elements: 

List of UI Elements
*******************

Containers
==========


<box>: Box
----------

Simplest container ever, can be scrollable ::

    @p('width', default=None)
    @p('height', default=None)
    @p('scroll', default=False, type=bool)


<pad>: Whitespace
-----------------

Adds a padding on four sides.


<indent>: Indentation
---------------------

Adds a padding on two sides.


<right>: Pull-to-right
----------------------

Pulls its content to right with ``float: right``


<hc>: Horizontal Container
--------------------------

A horizontal stacking container


<vc>: Vertical Container
------------------------

A vertical stacking container


<formline>: Form Line
---------------------

.. image:: /_static/dev/ui-elements/formline.png

Container for form controls, has a caption ::

    @p('text', default='', bindtypes=[str, unicode])


<formgroup>: Form Group
-----------------------

.. image:: /_static/dev/ui-elements/formgroup.png

Provides a nice form section separator ::

    @p('text', default='', bindtypes=[str, unicode])


<dt>, <dtr>, <dth> <dtd>: Data Table
------------------------------------

.. image:: /_static/dev/ui-elements/dt.png

A lined table ::

    <dt>
        <dtr>
            <dth text="Header" />
        </dtr>
        <dtr>
            <dtd>
                <label text="Child" />
            </dtd>
        </dtr>
    </dt>


<collapserow>: Collapsible Table Row
------------------------------------

A click-to expand table row ::

    <dt>
        <collapserow>
            <label text="Header Child" />
            <label text="Body Child" />
        </collapserow>
    </dt>

First child is a header and always visible. Second is the collapsible body. ::
    
    @p('expanded', default=False, type=bool, bindtypes=[bool])


<lt>, <ltr>, <ltd>: Layout Table
--------------------------------

An invisible layout grid (no padding).


<sortabledt>: Sortable Data Table
---------------------------------

.. image:: /_static/dev/ui-elements/sortabledt.png

User will be able to reorder rows ::

    <sortabledt>
        <dtr>
            <dtd>
                <label text="Child 1" />
            </dtd>
        </dtr>
        <dtr>
            <dtd>
                <label text="Child 2" />
            </dtd>
        </dtr>
        <dtr>
            <dtd>
                <label text="Child 3" />
            </dtd>
        </dtr>
    </sortabledt>

    @p('sortable', default=True, type=bool)
    @p('order', default='', type=str)

The **order** property holds the reordered element indexes (``[2,1,3]`` as seen on the image)


<tabs>, <tab>: Tabs
-------------------

.. image:: /_static/dev/ui-elements/tabs.png

User will be able to reorder rows ::

    <tabs>
        <tab title="1">                       
            <label text="Child 1" />                        
        </tab>
        <tab title="2">                       
            <label text="Child 2" />                        
        </tab>
        <tab title="3">                       
            <label text="Child 3" />                        
        </tab>
    </tabs>

    <tabs>:
    @p('active', default=0)

    <title>:
    @p('title', default='', bindtypes=[str, unicode])



Standard Controls
=================

<label>: Label
--------------

    @p('text', default='', bindtypes=[str, unicode, int, float])


<button>: Button
----------------

.. image:: /_static/dev/ui-elements/button.png 

::

    @p('text', default='', bindtypes=[str, unicode])
    @p('icon', default=None)
    @p('warning', default=None)  # display a warning text before click

    click()  # fired on click



<icon>: Inline Icon
-------------------

Icon IDs in Ajenti are coming from this page: http://fortawesome.github.io/Font-Awesome/icons/

    @p('icon', default=None, bindtypes=[str, unicode])


<tooltip>: Tooltip
------------------

.. image:: /_static/dev/ui-elements/tooltip.png

::

    @p('text', default='', bindtypes=[str, unicode, int])


<progressbar>: Progress Bar
---------------------------

.. image:: /_static/dev/ui-elements/progressbar.png

::

    @p('width', default=None)
    @p('value', default=0, type=float, bindtypes=[float]) # between 0.0 and 1.0
    


<list>, <listitem>: Lists
-------------------------

.. image:: /_static/dev/ui-elements/list.png

A list with clickable items::

    <list>
        <listitem>
            <label text="child" />
        </listitem>
        <listitem>
            <label text="child" />
        </listitem>
        <listitem>
            <label text="child" />
        </listitem>
    </list>

    <listitem>:
    click()  # fired on click


Inputs
======

<textbox>: Textbox
------------------

::

    @p('value', default='', bindtypes=[str, unicode, int])
    @p('type', default='text')  # or 'integer'


<editable>: Editable Label
--------------------------

.. image:: /_static/dev/ui-elements/editable.png

A label that becomes textbox when clicked::

    @p('value', default='', bindtypes=[str, unicode])
    @p('icon', default=None)


<checkbox>: Checkbox
--------------------

::

    @p('text', default='')
    @p('value', default=False, bindtypes=[bool])
    

<dropdown>: Dropdown Select
---------------------------

::

    @p('labels', default=[], type=list) 
    @p('values', default=[], type=list)
    @p('value', default='', bindtypes=[str, int, unicode])


<combobox>: Combo Box
---------------------

::

    @p('labels', default=[], type=list)
    @p('values', default=[], type=list)
    @p('separator', default=None, type=str) # if set, combobox becomes autocomplete-multiple-input-box
    @p('value', default='', bindtypes=[str, unicode])

Angular: ajenti.augeas
**********************

Services
========

.. js:class:: augeas

    .. js:function:: get(endpoint)

        Reads an Augeas tree from server side.

        :returns: promise → AugeasConfig

    .. js:function:: set(endpoint, config)

        Overwrites an Augeas tree on the server side.

        :returns: promise


.. js:class:: AugeasNode

    .. js:data:: name
    
    .. js:data:: value
    
    .. js:data:: parent

    .. js:data:: children

    .. js:function:: fullPath()


.. js:class:: AugeasConfig

    This is a JS doppelganger of normal Augeas API. In particular, it doesn't support advanced XPath syntax, and operates with regular expressions instead.

    .. js:function:: get(path)

        :returns: :class:`AugeasNode`

    .. js:function:: set(path, value)

    .. js:function:: model(path)

        :returns: a getter/setter function suitable for use as a ``ngModel``

    .. js:function:: insert(path, value, index)

    .. js:function:: remove(path)

    .. js:function:: match(path)

        :returns: ``Array(string)``

    .. js:function:: matchNodes(path)

        :returns: ``Array(AugeasNode)``



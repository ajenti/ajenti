Angular: ajenti.filesystem
**************************

Services
========

.. js:class:: filesystem

    .. js:function:: read(path)

        :returns: promise → content of ``path``

    .. js:function:: write(path, content)

        :returns: promise

    .. js:function:: list(path)

        :returns: promise → array

    .. js:function:: stat(path)

        :returns: promise → object

    .. js:function:: chmod(path, mode)

        :param int mode: numeric POSIX file mode
        :returns: promise

    .. js:function:: createFile(path, mode)

        :param int mode: numeric POSIX file mode
        :returns: promise

    .. js:function:: createDirectory(path, mode)

        :param int mode: numeric POSIX file mode
        :returns: promise

    .. js:function:: downloadBlob(content, mime, name)

        Launches a browser-side file download

        :param string content: Raw file content
        :param string mime: MIME type used
        :param string name: Default file name for saving
        :returns: promise

Directives
==========

.. js:function:: file-dialog

    File open/save dialog. Example::

        <file-dialog
            mode="open"
            ng:show="openDialogVisible"
            on-select="open(item.path)"
            on-cancel="openDialogVisible = false">
        </file-dialog>

        <file-dialog
            mode="save"
            ng:show="saveDialogVisible"
            on-select="saveAs(path)"
            on-cancel="saveDialogVisible = false"
            name="saveAsName">
        </file-dialog>


    :param expression ngShow:
    :param expression(item) onSelect: called after opening or saving a file. ``item`` is an object with a ``path`` property.
    :param expression onCancel: (optional) handler for the cancel button
    :param string mode: one of ``open``, ``save``
    :param binding name: (optional) name for the saved file
    :param binding path: (optional) current


.. js:function:: path-selector

    An input with a file selection dialog::

        <path-selector ng:model="filePath"></path-selector>

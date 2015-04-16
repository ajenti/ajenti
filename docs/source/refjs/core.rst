Angular: ajenti.core
********************

This Angular module contains core components of Ajenti frontend.


Services
--------


.. js:class:: config

    .. js:data:: data

        Config file content object

    .. js:function:: load()

        Gets complete configuration data of the backend

        :returns: promise

    .. js:function:: save()

        Updates and saves configuration data

        :returns: promise

    .. js:function:: getUserConfig()

        Gets per-user configuration data of the backend

        :returns: promise → per-user Ajenti config object

    .. js:function:: setUserConfig(config)

        Updates and saves per-user configuration data

        :param object config: updated configuration data from ``getUserConfig()``
        :returns: promise


.. js:class:: core

    .. js:function:: pageReload()

        Reloads the current URL

    .. js:function:: restart()

        Restarts the Ajenti process

.. js:class:: hotkeys

    Captures shortcut key events

    .. js:data:: ENTER, ESC

        Respective key codes

    .. js:function:: on(scope, handler, mode='keydown')

        Registers a hotkey handler in the provided ``scope``

        :param $scope scope: ``$scope`` to install handler into
        :param function(keyCode,\ rawEvent) handler: handler function. If the function returns a truthy value, event is cancelled and other handlers aren't notified.
        :param string mode: one of ``keydown``, ``keypress`` or ``keyup``.

.. js:class:: identity

    Provides info on the authentication status and user/machine identity

    .. js:data:: user

        Name of the logged in user

    .. js:data:: effective

        Effective UID of the server process

    .. js:data:: machine.name

        User-provided name of the machine

    .. js:data:: isSuperuser

        Whether current user is a superuser or not

    .. js:function:: auth(username, password, mode)

        Attempts to authenticate current session as ``username:password`` with a ``mode`` of ``normal`` or ``sudo``

    .. js:function:: login()

        Redirects user to a login dialog

    .. js:function:: logout()

        Deauthenticates current session

    .. js:function:: elevate()

        Redirects user to a sudo elevation dialog


.. js:class:: messagebox

    Provides interface to modal messagebox engine

    .. js:function:: show(options)

        Opens a new messagebox.

        :param object options:
        :param string options.title:
        :param string options.text:
        :param string options.positive: positive action button text. Clicking it will resolve the returned promise.
        :param string options.negative: negative action button text. Clicking it will reject the returned promise.
        :param string options.template: (optional) custom body template
        :param boolean options.scrollable: whether message body is scrollable
        :param boolean options.progress: whether to display an indeterminate progress indicator in the message

        :returns: a Promise-like object with an additional ``close()`` method.


.. js:class:: notify

    .. js:function:: info(title, text)
    .. js:function:: success(title, text)
    .. js:function:: warning(title, text)
    .. js:function:: error(title, text)

        Shows an appropriately styled notification

    .. js:function:: custom(style, title, text, url)

        Shows a clickable notification leading to ``url``.


.. js:class:: pageTitle

    Alters page ``<title>`` and global heading.

    .. js:function:: set(text)

        Sets title text

    .. js:function:: set(expression, scope)

        Sets an title expression to be watched. Example::

            $scope.getTitle = (page) -> someService.getPageTitle(page)
            $scope.page = ...

            pageTitle.set("getTitle(page)", $scope)


.. js:class:: push

    Processes incoming push messages (see :class:`aj.plugins.core.api.push`). This service has no public methods.

    This service broadcasts events that can be received as::

        $scope.$on 'push:pluginname', (message) ->
            processMessage(message)...


.. js:class:: tasks

    An interface to the tasks engine (see :class:`aj.plugins.core.api.tasks`).

    .. js:data:: tasks

        A list of task descriptors for the currently running tasks. Updated automatically.

    .. js:function:: start(cls, args, kwargs)

        Starts a server-side task.

        :param string cls: full task class name (``aj.plugins.pluginname....``)
        :param array args: task arguments
        :param object kwargs: task keyword arguments
        :returns: a promise, resolved once the task actually starts


Directives
----------

.. js:function:: autofocus

    Automatically focuses the input. Example::

        <input type="text" autofocus ng:model="..." />


.. js:function:: checkbox

    Renders a checkbox. Example::

        <span checkbox ng:model="..." text="Enable something"></span>


.. js:function:: dialog

    A modal dialog

    Example::

        <dialog ng:show="showDialog">
            <div class="modal-header">
                <h4>
                    Heading
                </h4>
            </div>
            <div class="modal-body scrollable">
                ...
            </div>
            <div class="modal-footer">
                <a ng:click="..." class="btn btn-default btn-flat">
                    Do something
                </a>
            </div>
        </dialog>

    :param expression ngShow:
    :param string dialogClass:



.. js:function:: floating-toolbar

    A toolbar pinned to the bottom edge. Example::

        <div class="floating-toolbar-padder"></div>

        <floating-toolbar>
            <a ng:click="..." class="btn btn-default btn-flat">
                Do something useful
            </a>
        </floating-toolbar>

        <!-- accented toolbar for selection actions -->

        <floating-toolbar class="accented" ng:show="haveSelectedItems">
            Some action buttons here
        </floating-toolbar>


.. js:function:: ng-enter

    Action handler for Enter key in inputs. Example::

        <input type="text" ng:enter="commitStuff()" ng:model="..." />


.. js:function:: progress-spinner


.. js:function:: root-access

    Blocks its inner content if the current user is not a superuser.


.. js:function:: smart-progress

    An improved version of ui-bootstrap's progressbar

    :param boolean animate:
    :param float value:
    :param float max:
    :param string text:
    :param string maxText:




Filters
-------

.. js:function:: bytesFilter(value, precision)

    :param int value: number of bytes
    :param int precision: number of fractional digits in the output
    :returns: string, e.g.: ``123.45 KB``

.. js:function:: ordinalFilter(value)

    :param int value:
    :returns: string, e.g.: ``121st``

.. js:function:: pageFilter(list, page, pageSize)

    Provides a page-based view on an array

    :param array list: input data
    :param int page: 1-based page index
    :param int pageSize: page size
    :returns: array

.. _man-about:

What's Ajenti and how it works
==============================

Ajenti Project itself consists of **Ajenti Core** itself and a set of stock plugins forming the **Ajenti Panel**.

Ajenti Core
-----------

Ajenti Core is a web interface development framework which includes a web server, IoC container, a simplistic web framework and set of core components aiding in client-server communications.

Ajenti Panel
------------

Ajenti Panel consists of plugins developed for the Ajenti Core and a startup script, together providing a server administration panel experience. The Panel's plugins include: file manager, terminal, notepad, etc.

Modus operandi
--------------

During bootstrap, Ajenti Core will locate and load Python modules containing Ajenti plugins (identified by a ``plugin.yml`` file). It will then register the implementation classes found in them in the root IoC container. Some interfaces to be implemented include :class:`aj.api.http.HttpPlugin`, :class:`aj.plugins.core.api.sidebar.SidebarItemProvider`.

Ajenti Core runs a HTTP server on a specified port, managing a pool of isolated session workers and forwarding requests to these workers, delivering them to the relevant :class:`aj.api.http.HttpPlugin` instances. It also supports Socket.IO connections, forwarding them to the relevant :class:`aj.api.http.SocketEndpoint` instances.

Ajenti contains a mechanism for session authentication through PAM login and ``sudo`` elevation. Standard ``core`` plugin provides HTTP API for that.

Authenticated sessions are moved to isolated worker processes running under the corresponding account. 

Ajenti frontend is an AngularJS application composed from Angular modules provided by each plugin. Every plugin can contribute its own JS/CSS code to the combined resource package delivered to the client. 

The ``core`` plugin provides a ``ng:view`` container for ``ngRoute`` navigation. So, the plugins that have UI are expected to provide additional ``ngRoute`` routes, templates and controllers.

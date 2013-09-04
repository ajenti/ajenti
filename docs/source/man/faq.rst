FAQ
===

How do I add domains/PHP/email accounts/websites?
-------------------------------------------------

Ajenti is a **server control** panel, not a **hosting control** panel. Please take a look at Virtualmin instead.

I forgot my password
--------------------

Open /etc/ajenti/config.json, look for your user entry, and replace whole password hash entry with a new plaintext password. Restart Ajenti. Click "save" under "Configuration" to rehash the password.

My OS isn't supported, but I'm a brave adventurer
-------------------------------------------------

::

    pip install ajenti
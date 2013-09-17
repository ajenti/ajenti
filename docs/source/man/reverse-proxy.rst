.. _reverse-proxy:

Reverse Proxying Ajenti
***********************

All Ajenti URLs are absolute and start with ``/ajenti:``, which makes it easy to reverse-proxy it with, for example, nginx::

    server {
        server_name fallthrough;
        client_max_body_size 20m;

        listen 80;

        location /ajenti {
            rewrite /ajenti/(.*) /$1 break;
            proxy_pass  http://127.0.0.1:8000;
            proxy_redirect / /ajenti/;
            proxy_set_header Host $host;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }
    }


For Apache, add following to your ``<Location>``::

    ProxyPass /ajenti http://localhost:8000
    ProxyPassMatch ^/(ajenti.*)$ http://localhost:8000/$1

    ProxyPassReverse /ajenti:static/ http://localhost:8000/ajenti:static/
    ProxyPassReverse /ajenti:auth http://localhost:8000/ajenti:auth
    ProxyPassReverse /ajenti http://localhost:8000
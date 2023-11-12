# Ajenti plugin DNS API

This plugin is attented to give an access to an external registrar API, like Gandi or GoDaddy, and manage the DNS entries.
Currently, there's only one [provider for the Gandi API](https://github.com/ajenti/ajenti/blob/master/plugins/dns_api/providers/gandi.py), but feel free to write your own provider for your registrar API.
The code should be enough commented to understand how it works.

## Configuration for the Gandi API

Just add the following entries in `/etc/ajenti/config.yml`:

```
dns_api:
  provider: gandi
  apikey: YOUR_API_KEY
```

and then restart `Ajenti`.

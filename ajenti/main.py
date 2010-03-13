import http
import plugin
import config

config.Load()
plugin.LoadPlugins()
http.Run()

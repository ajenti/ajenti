# coding=utf-8

config_templates = {
    'main': '',
    'jails': 'enable = true\n',
    'actions': """
# Fail2Ban configuration file
#
# Author:
#
#

[Definition]

# Option:  actionstart
# Notes.:  command executed once at the start of Fail2Ban.
# Values:  CMD
#
actionstart =


# Option:  actionstop
# Notes.:  command executed once at the end of Fail2Ban
# Values:  CMD
#
actionstop =


# Option:  actioncheck
# Notes.:  command executed once before each actionban command
# Values:  CMD
#
actioncheck =


# Option:  actionban
# Notes.:  command executed when banning an IP. Take care that the
#          command is executed with Fail2Ban user rights.
# Tags:    See jail.conf(5) man page
# Values:  CMD
#
actionban =


# Option:  actionunban
# Notes.:  command executed when unbanning an IP. Take care that the
#          command is executed with Fail2Ban user rights.
# Tags:    See jail.conf(5) man page
# Values:  CMD
#
actionunban =

[Init]

# Option:  port
# Notes.:  specifies port to monitor
# Values:  [ NUM | STRING ]
#
port =

# Option:  localhost
# Notes.:  the local IP address of the network interface
# Values:  IP
#
localhost = 127.0.0.1


# Option:  blocktype
# Notes.:  How to block the traffic. Use a action from man 5 ipfw
#          Common values: deny, unreach port, reset
# Values:  STRING
#
blocktype = unreach port

""",
    'filters': '# Fail2Ban filter\n[INCLUDES]\nbefore =\nafter =\n[Definition]\nfailregex =\n\nignoreregex =\n#Autor:',
    'extra': ''
}
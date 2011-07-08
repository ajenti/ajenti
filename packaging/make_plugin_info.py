#!/usr/bin/env python
import os
import commands

def shell(s):
    commands.getstatusoutput(s)

shell('mkdir meta/plugins -p')
for s in os.listdir('../plugins'):
    print '> '+s
    shell('mkdir meta/plugins/'+s)
    shell('cp ../plugins/%s/__init__.py meta/plugins/%s'%(s,s))
    shell('cp ../plugins/%s/files/icon.png meta/plugins/%s'%(s,s))
    shell('cd ../plugins; tar -cz %s > plugin.tar.gz'%s)
    shell('mv ../plugins/plugin.tar.gz meta/plugins/%s'%s)
    

import os
import subprocess
import re

from ajenti.api import *
from ajenti.plugins.main.api import SectionPlugin
from ajenti.ui import on
from ajenti.ui.binder import Binder
from ajenti.util import platform_select

class Repository (object):
    def __init__(self, name):
        self.name = name
        self.rwusers = ''
        self.rousers = '@all'


class User (object):
    def __init__(self, name, pubkey):
        self.name = name
        self.pubkey = pubkey

#class Group (object):
#    def __init__(self, name):
#        self.name = name
#        self.members = []


@plugin
class GitPlugin (SectionPlugin):
    user = 'gitolite3'
    keydir = '/var/lib/gitolite3/.gitolite/keydir/'
    confdir = '/var/lib/gitolite3/.gitolite/conf/'
    conf = 'gitolite.conf'


    def init(self):
        self.title = _('Git')
        self.icon = 'folder-close'
        self.category = 'Software'
        self.append(self.ui.inflate('git:main'))
        self.binder = Binder(None, self)
        self.find('usercollection').new_item = lambda c: User('newuser', '')
        self.find('repocollection').new_item = lambda c: Repository('newrepo')

        os.remove(self.confdir + self.conf)
        with open((self.confdir + self.conf), 'w+') as file:
            file.write('include "*.conf"')

    def on_page_load(self):
        self.refresh()

    def refresh(self):
        self.refresh_users()
        self.refresh_repositories()
        self.binder.setup(self).populate()



    def refresh_repositories(self):
        self.repositories = []

        userlist = []
        for user in self.users:
            userlist.append(user.name)
        self.find('rwusers').values = userlist
        self.find('rwusers').labels = userlist
        self.find('rousers').values = userlist
        self.find('rousers').labels = userlist

        for repoFile in os.listdir(self.confdir):
            if os.path.isfile(self.confdir + repoFile) and not self.conf in repoFile:
                with open(self.confdir + repoFile) as file:
                    content = file.read()
                    repo = Repository('')

                    # Repository Name
                    match = re.search(r'repo[\s]+([A-z0-9]+)', content, re.I)
                    repo.name = match.group(1)

                    #Repository Users(read-write)
                    match = re.search(r'RW\+[\s]+\=[\s]+([^\n]+)', content, re.I)
                    repo.rwusers = match is not None and match.group(1) or ''

                    #Repository Users(read-only)
                    match = re.search(r'R[\s]+\=[\s]+([^\n]+)', content, re.I)
                    repo.rousers = match is not None and match.group(1) or ''

                    self.repositories.append(repo)


    def refresh_users(self):
        self.users = []

        for userFile in os.listdir(self.keydir):
            with open(self.keydir + userFile) as file:
                username = userFile.replace('.pub', '')
                pubkey = file.read()

                self.users.append(User(username, pubkey))

    def reload(self):
        subprocess.call('su -c "gitolite compile" ' + self.user, shell=True)
        self.context.notify('info', _('Saved'))


    @on('save-repositories', 'click')
    def saveRepositories(self):
        self.binder.update()

        files = []
        for file in os.listdir(self.confdir):
            if os.path.isfile(self.confdir + file) and not "gitolite.conf" in file:
                files.append(file)

        for repo in self.repositories:
            with open((self.confdir + repo.name + '.conf'), 'w+') as file:
                content = 'repo '
                content += repo.name
                content += '\n'

                rwusers = repo.rwusers.strip()
                if len(rwusers) > 0:
                    content += '\tRW+\t=\t' + rwusers + '\n'

                rousers = repo.rousers.strip()
                if len(rousers) > 0:
                    content += '\tR\t=\t' + rousers + '\n'

                file.write(content)

            if (repo.name + '.conf') in files:
                files.remove(repo.name + '.conf')

        for file in files:
            os.remove(self.confdir + file)

        self.reload()

    @on('save-users', 'click')
    def saveUsers(self):
        self.binder.update()

        files = []
        for file in os.listdir(self.keydir):
            files.append(file)

        for user in self.users:
            with open((self.keydir + user.name + '.pub'), 'w+') as file:
                file.write(user.pubkey)
            if (user.name + '.pub') in files:
                files.remove(user.name + '.pub')

        for file in files:
            os.remove(self.keydir + file)

        self.reload();





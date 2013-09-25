import os
import stat
import itertools
import subprocess

from ajenti.api import *
from ajenti.plugins.main.api import SectionPlugin
from ajenti.ui import on
from ajenti.ui.inflater import TemplateNotFoundError
from ajenti.ui.binder import Binder, CollectionAutoBinding

from ajenti.plugins.network.api import NetworkManager

from reconfigure.configs import IPTablesConfig
from reconfigure.items.iptables import TableData, ChainData, RuleData, OptionData


@interface
class FirewallManager (object):
    def get_autostart_state(self):
        pass

    def set_autostart_state(self, state):
        pass


@plugin
class DebianFirewallManager (FirewallManager):
    platforms = ['debian']
    autostart_script_path = '/etc/network/if-up.d/iptables'
    config_path = '/etc/iptables.up.rules'
    config_path_ajenti = '/etc/iptables.up.rules.ajenti'

    def get_autostart_state(self):
        return os.path.exists(self.autostart_script_path)

    def set_autostart_state(self, state):
        if state and not self.get_autostart_state():
            open(self.autostart_script_path, 'w').write("""#!/bin/sh
            iptables-restore < %s
            """ % self.config_path)
            os.chmod(self.autostart_script_path, stat.S_IRWXU | stat.S_IRWXO)
        if not state and self.get_autostart_state():
            os.unlink(self.autostart_script_path)


@plugin
class CentOSFirewallManager (FirewallManager, BasePlugin):
    platforms = ['centos']
    config_path = '/etc/sysconfig/iptables'
    config_path_ajenti = '/etc/iptables.up.rules.ajenti'

    def get_autostart_state(self):
        return True

    def set_autostart_state(self, state):
        self.context.notify('info', _('You can\'t disable firewall autostart on this platform'))


@plugin
class Firewall (SectionPlugin):
    platforms = ['centos', 'debian']

    def init(self):
        self.title = _('Firewall')
        self.icon = 'fire'
        self.category = _('System')

        self.append(self.ui.inflate('iptables:main'))

        self.fw_mgr = FirewallManager.get()
        self.config = IPTablesConfig(path=self.fw_mgr.config_path_ajenti)
        self.binder = Binder(None, self.find('config'))

        self.find('tables').new_item = lambda c: TableData()
        self.find('chains').new_item = lambda c: ChainData()
        self.find('rules').new_item = lambda c: RuleData()
        self.find('options').new_item = lambda c: OptionData()
        self.find('options').binding = OptionsBinding
        self.find('options').filter = lambda i: not i.name in ['j', 'jump']

        def post_rule_bind(o, c, i, u):
            u.find('add-option').on('change', self.on_add_option, c, i, u)
            action = ''
            j_option = i.get_option('j', 'jump')
            if j_option:
                action = j_option.arguments[0].value
            u.find('action').text = action
            u.find('action').style = 'iptables-action iptables-%s' % action
            u.find('action-select').value = action
            u.find('title').text = i.comment if i.comment else i.summary

        def post_rule_update(o, c, i, u):
            action = u.find('action-select').value
            j_option = i.get_option('j', 'jump')
            if j_option:
                j_option.arguments[0].value = action
            else:
                if action:
                    o = OptionData.create_destination()
                    o.arguments[0].value = action
                    i.options.append(o)

        self.find('rules').post_item_bind = post_rule_bind
        self.find('rules').post_item_update = post_rule_update

        self.find('add-option').values = self.find('add-option').labels = [_('Add option')] + sorted(OptionData.templates.keys())

    def on_page_load(self):
        if not os.path.exists(self.fw_mgr.config_path_ajenti):
            if not os.path.exists(self.fw_mgr.config_path):
                open(self.fw_mgr.config_path, 'w').write("""
*mangle
:PREROUTING ACCEPT [0:0]
:INPUT ACCEPT [0:0]
:FORWARD ACCEPT [0:0]
:OUTPUT ACCEPT [0:0]
:POSTROUTING ACCEPT [0:0]
COMMIT
*nat
:PREROUTING ACCEPT [0:0]
:INPUT ACCEPT [0:0]
:OUTPUT ACCEPT [0:0]
:POSTROUTING ACCEPT [0:0]
COMMIT
*filter
:INPUT ACCEPT [0:0]
:FORWARD ACCEPT [0:0]
:OUTPUT ACCEPT [0:0]
COMMIT

                """)
            open(self.fw_mgr.config_path_ajenti, 'w').write(open(self.fw_mgr.config_path).read())
        self.config.load()
        self.refresh()

    @on('load-current', 'click')
    def on_load_current(self):
        subprocess.call('iptables-save > %s' % self.fw_mgr.config_path, shell=True)
        self.config.load()
        self.refresh()

    def refresh(self):
        self.find('autostart').text = (_('Disable') if self.fw_mgr.get_autostart_state() else _('Enable')) + _(' autostart')

        self.binder.reset(self.config.tree)
        actions = ['ACCEPT', 'DROP', 'REJECT', 'LOG', 'MASQUERADE', 'DNAT', 'SNAT'] + \
            list(set(itertools.chain.from_iterable([[c.name for c in t.chains] for t in self.config.tree.tables])))
        self.find('action-select').labels = actions
        self.find('action-select').values = actions
        self.find('chain-action-select').labels = actions
        self.find('chain-action-select').values = actions
        self.binder.autodiscover().populate()

    @on('autostart', 'click')
    def on_autostart_change(self):
        self.fw_mgr.set_autostart_state(not self.fw_mgr.get_autostart_state())
        self.refresh()

    def on_add_option(self, options, rule, ui):
        o = OptionData.create(ui.find('add-option').value)
        ui.find('add-option').value = ''
        rule.options.append(o)
        self.binder.populate()

    @on('save', 'click')
    def save(self):
        self.binder.update()

        for t in self.config.tree.tables:
            for c in t.chains:
                for r in c.rules:
                    r.verify()

        self.config.save()

        open(self.fw_mgr.config_path, 'w').write(
            ''.join(
                l.split('#')[0] + '\n'
                for l in
                open(self.fw_mgr.config_path_ajenti).read().splitlines()
            )
        )
        self.refresh()
        self.context.notify('info', _('Saved'))

    @on('edit', 'click')
    def raw_edit(self):
        self.context.launch('notepad', path='/etc/iptables.up.rules')

    @on('apply', 'click')
    def apply(self):
        self.save()
        cmd = 'cat %s | iptables-restore' % self.fw_mgr.config_path
        if subprocess.call(cmd, shell=True) != 0:
            self.context.launch('terminal', command=cmd)
        else:
            self.context.notify('info', _('Applied successfully'))


class OptionsBinding (CollectionAutoBinding):
    option_map = {
        's': 'source',
        'src': 'source',
        'i': 'in-interface',
        'o': 'out-interface',
        'sport': 'source-port',
        'dport': 'destination-port',
        'sports': 'source-ports',
        'dports': 'destination-ports',
        'm': 'match',
        'p': 'protocol',
    }

    template_map = {
        'source': 'address',
        'destination': 'address',
        'mac-source': 'address',
        'in-interface': 'interface',
        'out-interface': 'interface',
        'source-port': 'port',
        'destination-port': 'port',
        'source-ports': 'ports',
        'destination-ports': 'ports',
    }

    def get_template(self, item, ui):
        root = ui.ui.inflate('iptables:option')

        option = item.name
        if option in OptionsBinding.option_map:
            option = OptionsBinding.option_map[option]
        item.name = option
        item.cmdline = '--%s' % option

        if option in OptionsBinding.template_map:
            template = OptionsBinding.template_map[option]
        else:
            template = option

        try:
            option_ui = ui.ui.inflate('iptables:option-%s' % template)
        except TemplateNotFoundError:
            option_ui = ui.ui.inflate('iptables:option-custom')

        if option_ui.find('device'):
            device = option_ui.find('device')
            device.values = device.labels = NetworkManager.get().get_devices()
        root.find('slot').append(option_ui)
        return root

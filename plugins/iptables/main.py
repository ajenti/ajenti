from ajenti.ui import *
from ajenti.com import implements
from ajenti.app.api import ICategoryProvider
from ajenti.app.helpers import *
from ajenti.utils import *

from backend import *


class FirewallPlugin(CategoryPlugin):
    text = 'Firewall'
    icon = '/dl/firewall/icon_small.png'
    folder = 'system'

    defactions = ['ACCEPT', 'DROP', 'REJECT', 'LOG', 'EXIT', 'MASQUERADE']


    def on_init(self):
        self.cfg = Config()
        self.cfg.load()

    def on_session_start(self):
        self._tab = 0
        self._shuffling = None
        self._shuffling_table = None
        self._adding_chain = None
        self._editing_table = None
        self._editing_chain = None
        self._editing_rule = None
        self._error = ''
        
    def get_ui(self):
        st = UI.HContainer( 
                UI.MiniButton(text='Apply', id='apply'),
                UI.WarningMiniButton(text='Load current', id='loadruntime', msg='Dispose saved configuration and load current iptables status'),
                UI.MiniButton(text='Autostart', id='autostart') 
                    if not self.cfg.has_autostart() else
                    UI.MiniButton(text='Disable autostart', id='noautostart'),
                spacing=0
             )
             
        panel = UI.PluginPanel(st, title='IPTables Firewall', icon='/dl/firewall/icon.png')
        panel.append(self.get_default_ui())
        return panel

    def get_default_ui(self):
        tc = UI.TabControl(active=self._tab)
        for t in self.cfg.tables:
            t = self.cfg.tables[t]
            vc = UI.VContainer(spacing=15)
            for ch in t.chains:
                ch = t.chains[ch]
                uic = UI.FWChain(tname=t.name, name=ch.name, default=ch.default)
                idx = 0
                for r in ch.rules:
                    uic.append(
                        UI.FWRule(
                            action=r.action, 
                            desc=r.desc if r.action in self.defactions else r.action, 
                            id='%s/%s/%i'%(t.name,ch.name,idx)
                        ))
                    idx += 1
                vc.append(uic)
            vc.append(UI.Button(text='Add new chain to '+t.name, id='addchain/'+t.name))
            tc.add(t.name, vc)
            
        ui = UI.VContainer()
        if self._error != '':
            ui.append(UI.ErrorBox(text=self._error, title='Can\'t apply config'))
            
        ui.append(UI.Label(size=3, text='Rule tables'))
        ui.append(tc)
             
        if self._shuffling != None:
            ui.append(self.get_ui_shuffler())
      
        if self._adding_chain != None:
            ui.append(UI.InputBox(id='dlgAddChain', text='Chain name:'))

        if self._editing_rule != None:
            ui.append(self.get_ui_edit_rule(
                        rule=self.cfg.tables[self._editing_table].\
                                      chains[self._editing_chain].\
                                      rules[self._editing_rule]
                    ))

        return ui

    def get_ui_edit_rule(self, rule=Rule()):
        protocols = (('TCP','tcp'), ('UDP','udp'), ('ICMP','icmp'))
        
        tc = UI.TabControl()
        tc.add('Main',
            UI.VContainer(
                UI.LayoutTable(
                    UI.LayoutTableRow(
                        UI.Label(text='Action:'),
                        UI.Radio(text='Accept', name='caction', value='ACCEPT', checked=rule.action=="ACCEPT"),
                        UI.Radio(text='Drop',   name='caction', value='DROP',   checked=rule.action=="DROP"),
                        UI.Radio(text='Reject', name='caction', value='REJECT', checked=rule.action=="REJECT"),
                        UI.Radio(text='Log',    name='caction', value='LOG',   checked=rule.action=="LOG"),
                    ),
                    UI.LayoutTableRow(
                        UI.Container(),
                        UI.Radio(text='Masq',   name='caction', value='MASQUERADE', checked=rule.action=="MASQUERADE"),
                        UI.Radio(text='Exit',   name='caction', value='EXIT',       checked=rule.action=="EXIT"),
                        UI.Radio(text='Run chain:', name='caction', value='RUN',    checked=rule.action not in self.defactions),
                        UI.TextInput(name='runchain', size=10, value=rule.action)
                    )
                ),
                UI.LayoutTable(
                    rule.get_ui_select('protocol', 'Protocol:', protocols, size=5),
                    rule.get_ui_text('source', 'Source address:', help="You can specify IP mask like 192.168.0.0/24"),
                    rule.get_ui_text('destination', 'Destination address:'),
                    rule.get_ui_text('mac_source', 'Source MAC address:'),
                    rule.get_ui_select('in_interface', 'Incoming interface:', self.cfg.get_devices(), size=7),
                    rule.get_ui_select('out_interface', 'Outgoing interface:', self.cfg.get_devices(), size=7),
                    rule.get_ui_bool('fragmented', 'Fragmentation:'),
                    UI.LayoutTableRow(           
                        UI.Label(text='Modules:'),
                        UI.LayoutTableCell(
                            UI.TextInput(name='modules', value=' '.join(rule.modules), help="Additional IPTables modules to load"),
                            colspan=2
                        )
                    ),
                    UI.LayoutTableRow(           
                        UI.Label(text='More options:'),
                        UI.LayoutTableCell(
                            UI.TextInput(name='options', value=' '.join(rule.miscopts)),
                            colspan=2
                        )
                    )
                )
            ))
            
        tc.add('TCP/UDP',
            UI.LayoutTable(
                rule.get_ui_text('sport', 'Source port:', help='Can accept lists and ranges like 80:85,8000 up to 15 ports'),
                rule.get_ui_text('dport', 'Destination port:'),
                rule.get_ui_flags('TCP flags:'),
                rule.get_ui_states('TCP states:'),
            ))
            
        return UI.DialogBox(tc, id='dlgEditRule', miscbtn='Delete', miscbtnid='deleterule')
        
    def get_ui_shuffler(self):
        li = UI.SortList(id='list')
        for r in self.cfg.tables[self._shuffling_table].chains[self._shuffling].rules:
            li.append(
                UI.SortListItem(
                    UI.FWRule(action=r.action, desc=r.desc, id=''), 
                    id=r.raw
                ))
            
        return UI.DialogBox(li, id='dlgShuffler')
               
    @event('minibutton/click')
    @event('button/click')
    def on_click(self, event, params, vars=None):
        if params[0] == 'apply':
            self._error = self.cfg.apply_now()
        if params[0] == 'autostart':
            self.cfg.set_autostart(True)
        if params[0] == 'noautostart':
            self.cfg.set_autostart(False)
        if params[0] == 'loadruntime':
            self.cfg.load_runtime()
        if params[0] == 'setdefault':
            self._tab = self.cfg.table_index(params[1])
            self.cfg.tables[params[1]].chains[params[2]].default = params[3]
            self.cfg.save()
        if params[0] == 'shuffle':
            self._tab = self.cfg.table_index(params[1])
            self._shuffling_table = params[1]
            self._shuffling = params[2]
        if params[0] == 'addchain':
            self._tab = self.cfg.table_index(params[1])
            self._adding_chain = params[1]
        if params[0] == 'deletechain':
            self._tab = self.cfg.table_index(params[1])
            self.cfg.tables[params[1]].chains.pop(params[2])
            self.cfg.save()
        if params[0] == 'addrule':
            self._tab = self.cfg.table_index(params[1])
            self._editing_table = params[1]
            self._editing_chain = params[2]
            ch = self.cfg.tables[self._editing_table].\
                         chains[self._editing_chain]
            self._editing_rule = len(ch.rules)
            ch.rules.append(Rule('-A %s -j ACCEPT'%params[2]))
            self.cfg.save()
            
        if params[0] == 'deleterule':
            self.cfg.tables[self._editing_table].\
                     chains[self._editing_chain].\
                     rules.pop(self._editing_rule)
            self._editing_chain = None
            self._editing_table = None
            self._editing_rule = None
            self.cfg.save()

    @event('fwrule/click')
    def on_fwrclick(self, event, params, vars=None):
        self._tab = self.cfg.table_index(params[0])
        self._editing_table = params[0]
        self._editing_chain = params[1]
        self._editing_rule = int(params[2])
          
    @event('dialog/submit')
    def on_submit(self, event, params, vars):
        if params[0] == 'dlgAddChain':
            if vars.getvalue('action', '') == 'OK':
                n = vars.getvalue('value', '')
                if n == '': return
                self.cfg.tables[self._adding_chain].chains[n] = Chain(n, '-')
                self.cfg.save()
            self._adding_chain = None
        if params[0] == 'dlgShuffler':
            if vars.getvalue('action', '') == 'OK':
                d = vars.getvalue('list', '').split('|')
                ch = self.cfg.tables[self._shuffling_table].chains[self._shuffling]
                ch.rules = []
                for s in d:
                    ch.rules.append(Rule(s))
                self.cfg.save()
            self._shuffling = None
            self._shuffling_table = None
        if params[0] == 'dlgEditRule':
            if vars.getvalue('action', '') == 'OK':
                self.cfg.tables[self._editing_table].\
                         chains[self._editing_chain].\
                          rules[self._editing_rule].apply_vars(vars)
                self.cfg.save()
            self._editing_chain = None
            self._editing_table = None
            self._editing_rule = None
            
class FirewallContent(ModuleContent):
    module = 'firewall'
    path = __file__
    widget_files = ['fw.xslt']
    css_files = ['fw.css']

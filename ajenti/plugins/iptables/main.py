from ajenti.api import *
from ajenti.plugins.main.api import SectionPlugin
from ajenti.ui import on
from ajenti.ui.inflater import TemplateNotFoundError
from ajenti.ui.binder import Binder, CollectionAutoBinding

from reconfigure.configs import IPTablesConfig
from reconfigure.items.iptables import TableData, ChainData, RuleData, OptionData, ArgumentData


@plugin
class Firewall (SectionPlugin):
    def init(self):
        self.title = 'Firewall'
        self.category = 'System'

        self.append(self.ui.inflate('iptables:main'))

        self.config = IPTablesConfig(path='/etc/iptables.up.rules')
        self.binder = Binder(None, self.find('config'))
        self.find('tables').new_item = lambda c: TableData()
        self.find('chains').new_item = lambda c: ChainData()
        self.find('rules').new_item = lambda c: RuleData()
        self.find('options').new_item = lambda c: OptionData()
        self.find('options').binding = OptionsBinding

        def post_rule_bind(o, c, i, u):
            u.find('add-option').on('change', self.on_add_option, c, i, u)
        self.find('rules').post_item_bind = post_rule_bind

        self.find('add-option').values = [''] + OptionData.templates.keys()
        self.find('add-option').labels = ['Add option'] + OptionData.templates.keys()

    def on_page_load(self):
        self.config.load()
        self.refresh()

    def refresh(self):
        self.binder.reset(self.config.tree).autodiscover().populate()

    def on_add_option(self, options, rule, ui):
        o = OptionData.create(ui.find('add-option').value)
        ui.find('add-option').value = ''
        rule.options.append(o)
        self.binder.populate()

    @on('save', 'click')
    def save(self):
        self.binder.update()
        self.config.save()


class OptionsBinding (CollectionAutoBinding):
    option_map = {
        's': 'source',
        'src': 'source',
    }

    def get_template(self, item, ui):
        root = ui.ui.inflate('iptables:option')
        try:
            option = item.name
            if option in OptionsBinding.option_map:
                option = OptionsBinding.option_map[option]
            item.name = option
            item.cmdline = '--%s' % option
            option_ui = ui.ui.inflate('iptables:option-%s' % option)
            root.find('slot').append(option_ui)
        except TemplateNotFoundError:
            pass
        return root

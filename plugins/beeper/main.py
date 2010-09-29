import platform
from pprint import pprint, pformat

from ajenti.ui import *
from ajenti import version
from ajenti.app.helpers import CategoryPlugin, ModuleContent, EventProcessor, event
from ajenti.app.session import SessionProxy

class BeeperContent(ModuleContent):
    module = 'beeper'
    path = __file__

class BeeperPlugin(CategoryPlugin):

    text = 'Beeper'
    description = 'Beep, beep, beep!'
    icon = '/dl/beeper/icon.png'
    
    def on_session_start(self):
        self._text = ''
        self._form_text = []
        self._dlg_visible = False
        self._tree = TreeManager()

    def get_ui(self):
        h = UI.HContainer(
                UI.Image(file='/dl/beeper/bigicon.png'),
                UI.Spacer(width=10),
                UI.VContainer(
                    UI.Label(text='Beeper', size=5),
                    UI.Label(text='Awesome beeping action')
                )
            )
        b = UI.Button(text='Beep!')
        b['id'] = 'beeper-btn-clickme'
        a = UI.Action(text='Bang!')
        a['description'] = 'Come on, click me!'
        a['icon'] = '/dl/core/ui/icon-ok.png'
        a['id'] = 'beeper-act-clickme'
        l = UI.LinkLabel(text='Boom!')
        l['id'] = 'beeper-ll-clickme'

        f = UI.VContainer()
        for s in self._form_text:
            f.append(UI.Text(s))

        dlg = UI.DialogBox(
                UI.LayoutTable(
                    UI.LayoutTableRow(
                        UI.LayoutTableCell(
                            UI.TextInput(name="someInput"),
                            UI.br(),
                            UI.Select(
                                UI.SelectOption(text="option1", value="1"),
                                UI.SelectOption(text="option2", value="2"),
                                name="select"
                            ),
                            UI.br(),
                            UI.TextInputArea(value='L\norem\nipsum dolor sit amet, consectetuer adipiscing elit. Maecenas feugiat consequat diam. Maecenas metus.', name='text', width=100, height=100),
                            rowspan="3"
                        ),
                        UI.Checkbox(name='vote', text='I wanna vote for:', checked='yes'),
                    ),
                    UI.LayoutTableRow(
                        UI.Radio(name='for', text='Checkboxes', value="checkbox"),
                    ),
                    UI.LayoutTableRow(
                        UI.Radio(name='for', text='Radio buttons', checked='yes', value="radio")
                    ),
                    UI.LayoutTableRow(
                        UI.SortList(
                            UI.SortListItem(UI.Label(text='Alpha'), id='a'),
                            UI.SortListItem(UI.Label(text='Bravo'), id='b'),
                            UI.SortListItem(UI.Label(text='Charlie'), id='c'),
                            UI.SortListItem(UI.Label(text='Delta'), id='d'),
                            id='list'
                        )
                    ),
                    UI.CustomHTML(html='<b>Hello</b> <i>HTML!</i>')
                ),
                title="Test Dialog", id="testDialog",
                hidecancel=True
            )

        b2 = UI.Button(text='Show dialog')
        b2['id'] = 'btn-dialog'

        tree =      UI.TreeContainer(
                        UI.TreeContainer(
                            UI.Label(text='789',id='123/456/789'),
                            UI.Label(text='101',id='123/456/101'),
                            text='456',id='123/456'
                        ),
                        UI.Label(text='112',id='123/112'),
                        text='123', id='123'
                    )
        self._tree.apply(tree)

        e = UI.ErrorBox(title='Panic!', text='This is SPARTAAA!!!')

        p = UI.HContainer(
                UI.VContainer(
                    h,
                    e,
                    UI.Spacer(height=20),
                    UI.Label(text=self._text),
                    b,
                    l,
                    a,
                    UI.Spacer(height=50),
                    UI.DataTable(
                        UI.DataTableRow(
                            UI.Label(text='Key'),
                            UI.Label(text='Value'),
                            header=True,
                        ),
                        UI.DataTableRow(
                            UI.Label(text='12'),
                            UI.Label(text='34')
                        ),
                        UI.DataTableRow(
                            UI.Label(text='56'),
                            UI.Label(text='78')
                        )
                    )
                ),
                UI.Spacer(width=30),
                UI.VContainer(
                    f,
                    b2,
                    dlg if self._dlg_visible else None,
                    tree
                )
            )

        return p

    @event('dialog/submit')
    def on_submit(self, event, params, vars=None):
        self._form_text = []
        self._form_text.append("You submited form: %s"%str(params[0]))
        self._form_text.append("Vars:")
        for k in vars.keys():
            if len(vars.getlist(k)) > 1:
                self._form_text.append("%s = [%s]\n"%(k, ', '.join(vars.getlist(k))))
            else:
                self._form_text.append("%s = %s\n"%(k, vars.getvalue(k,'')))
        self._dlg_visible = False

    @event('button/click')
    def on_click(self, event, params, vars=None):
        if params[0] == 'beeper-btn-clickme':
            self._text += 'Beep! '
            print 'Clicked button!'
            pprint(params)
            pprint(vars)
        if params[0] == 'btn-dialog':
            self._dlg_visible = True

    @event('action/click')
    def on_aclick(self, event, params, vars=None):
        if params[0] == 'beeper-act-clickme':
            self._text += 'Bang! '
            print 'Clicked action!'
            pprint(params)
            pprint(vars)

    @event('linklabel/click')
    def on_lclick(self, event, params, vars=None):
        pprint(params)
        pprint(vars)
        if params[0] == 'beeper-ll-clickme':
            self._text += 'Boom! '
            print 'Clicked link!'
            pprint(params)
            pprint(vars)

    @event('treecontainer/click')
    def on_tclick(self, event, params, vars=None):
        self._tree.node_click('/'.join(params))
        return ''
        

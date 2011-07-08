from ajenti.ui import *
from ajenti.com import implements
from ajenti.api import *
from ajenti.utils import *

import backend


class FSPlugin(CategoryPlugin):
    text = 'Filesystems'
    icon = '/dl/filesystems/icon.png'
    folder = 'system'

    def on_init(self):
        self.fstab = backend.read()

    def on_session_start(self):
        self._editing = -1

    def get_ui(self):
        ui = self.app.inflate('filesystems:main')
        
        t = ui.find('list')
        
        for u in self.fstab:
            t.append(UI.DataTableRow(
                    UI.Label(text=u.src, bold=True),
                    UI.Label(text=u.dst),
                    UI.Label(text=u.fs_type),
                    UI.Label(text=u.options),
                    UI.Label(text=str(u.dump_p)),
                    UI.Label(text=str(u.fsck_p)),
                    UI.DataTableCell(
                        UI.HContainer(
                            UI.MiniButton(id='edit/'+str(self.fstab.index(u)), text='Edit'),
                            UI.WarningMiniButton(id='del/'+str(self.fstab.index(u)), text='Delete', msg='Remove %s from fstab'%u.src)
                        ),
                        hidden=True
                    )
                ))

        if self._editing != -1:
            try:
                e = self.fstab[self._editing]
            except:
                e = backend.Entry()
                e.src = '/dev/sda1'
                e.dst = '/tmp'
                e.options = 'none'
                e.fs_type = 'none'
                e.dump_p = 0
                e.fsck_p = 0
            self.setup_ui_edit(ui, e)
            
        else:
            ui.remove('dlgEdit')
            
        return ui

    def get_ui_sources_list(self, e):
        lst = UI.Select(name='disk')
        cst = True
        for p in backend.list_partitions():
            s = p
            try:
                s += ': %s partition %s' % (backend.get_disk_vendor(p), p[-1])
            except:
                pass
            sel = e != None and e.src == p
            cst &= not sel
            lst.append(UI.SelectOption(value=p, text=s, selected=sel))
        for p in backend.list_partitions():
            u = backend.get_partition_uuid_by_name(p)
            if u != '':
                s = 'UUID=' + u
                sel = e != None and e.src == s
                cst &= not sel
                lst.append(UI.SelectOption(value=s, text=p+': '+u , selected=sel))

        lst.append(UI.SelectOption(text='proc', value='proc', selected=e.src=='proc'))
        cst &= e.src != 'proc'
        lst.append(UI.SelectOption(text='Custom', value='custom', selected=cst))
        return lst, cst

    def setup_ui_edit(self, ui, e):
        opts = e.options.split(',')
        bind = False
        ro = False
        loop = False
        if 'bind' in opts:
            opts.remove('bind')
            bind = True
        if 'ro' in opts:
            opts.remove('ro')
            ro = True
        if 'loop' in opts:
            opts.remove('loop')
            loop = True
        opts = ','.join(opts)

        lst,cst = self.get_ui_sources_list(e)
        ui.append('sources', lst)
        ui.find('src').set('value', e.src if cst else '')
        ui.find('mp').set('value', e.dst)
        ui.find('fs').set('value', e.fs_type)
        ui.find('opts').set('value', e.options)
        ui.find('ro').set('checked', ro)
        ui.find('bind').set('checked', bind)
        ui.find('loop').set('checked', loop)
        ui.find('dump_p').set('value', e.dump_p)
        ui.find('fsck_p').set('value', e.fsck_p)

    @event('minibutton/click')
    @event('button/click')
    @event('linklabel/click')
    def on_click(self, event, params, vars=None):
        if params[0] == 'add':
            self._editing = len(self.fstab)
        if params[0] == 'edit':
            self._editing = int(params[1])
        if params[0] == 'del':
            self.fstab.pop(int(params[1]))
            backend.save(self.fstab)

    @event('dialog/submit')
    def on_submit(self, event, params, vars=None):
        if params[0] == 'dlgEdit':
            v = vars.getvalue('value', '')
            if vars.getvalue('action', '') == 'OK':
                e = backend.Entry()
                if vars.getvalue('disk', 'custom') == 'custom':
                    e.src = vars.getvalue('src', 'none')
                else:
                    e.src = vars.getvalue('disk', 'none')
                e.dst = vars.getvalue('mp', 'none')
                e.fs_type = vars.getvalue('fs', 'none')
                e.options = vars.getvalue('opts', '')
                if vars.getvalue('bind', '0') == '1':
                    e.options += ',bind'
                if vars.getvalue('loop', '0') == '1':
                    e.options += ',loop'
                if vars.getvalue('ro', '0') == '1':
                    e.options += ',ro'
                e.options = e.options.strip(',')
                if e.options.startswith('none,'):
                    e.options = e.options[5:]

                e.dump_p = int(vars.getvalue('dump_p', '0'))
                e.fsck_p = int(vars.getvalue('fsck_p', '0'))
                try:
                    self.fstab[self._editing] = e
                except:
                    self.fstab.append(e)
                backend.save(self.fstab)
            self._editing = -1


from ajenti.ui import *
from ajenti.com import implements
from ajenti.app.api import ICategoryProvider
from ajenti.app.helpers import *
from ajenti.utils import *

import backend


class FSPlugin(CategoryPlugin):
    implements (ICategoryProvider)

    text = 'Filesystems'
    icon = '/dl/filesystems/icon_small.png'
    folder = 'system'
        
    def on_init(self):
        self.fstab = backend.read()
        
    def on_session_start(self):
        self._log = ''
        self._editing = -1
        
    def get_ui(self):
        panel = UI.PluginPanel(UI.Label(text=self._log), title='Mounted filesystems', icon='/dl/filesystems/icon.png')

        panel.appendChild(self.get_default_ui())        

        return panel

    def get_default_ui(self):
        t = UI.DataTable(UI.DataTableRow(
                UI.Label(text='Source'),
                UI.Label(text='Mountpoint'),
                UI.Label(text='FS type'),
                UI.Label(text='Options'),
                UI.Label(),
                UI.Label(),
                UI.Label(), header=True
               ))
        for u in self.fstab:       
            t.appendChild(UI.DataTableRow(
                    UI.Label(text=u.src, bold=True),
                    UI.Label(text=u.dst),
                    UI.Label(text=u.fs_type),
                    UI.Label(text=u.options),
                    UI.Label(text=str(u.dump_p)),
                    UI.Label(text=str(u.fsck_p)),
                    UI.DataTableCell(
                        UI.HContainer(
                            UI.MiniButton(id='edit/'+str(self.fstab.index(u)), text='Edit'),
                            UI.WarningMiniButton(id='del/'+str(self.fstab.index(u)), text='Delete')
                        ),
                        hidden=True
                    )
                ))
                
        t = UI.VContainer(t, UI.Button(text='Add mount', id='add'))
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
            t.vnode(self.get_ui_edit(e))
            
        return t
        
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
            lst.appendChild(UI.SelectOption(value=p, text=s, selected=sel))
        for p in backend.list_partitions():
            u = backend.get_partition_uuid_by_name(p)
            if u != '':
                s = 'UUID=' + u
                sel = e != None and e.src == s
                cst &= not sel
                lst.appendChild(UI.SelectOption(value=s, text=p+': '+u , selected=sel))

        lst.appendChild(UI.SelectOption(text='proc', value='proc', selected=e.src=='proc'))  
        cst &= e.src != 'proc'  
        lst.appendChild(UI.SelectOption(text='Custom', value='custom', selected=cst))    
        return lst, cst
                
    def get_ui_edit(self, e):
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
        
        t = UI.VContainer(  
              UI.LayoutTable(
                    UI.LayoutTableRow(
                        UI.Label(text='Source: '),
                        lst
                    ),
                    UI.LayoutTableRow(
                        UI.Label(),
                        UI.TextInput(name='src', value=e.src if cst else '')
                    ),
                    UI.LayoutTableRow(
                        UI.Label(text='Mount point: '),
                        UI.TextInput(name='mp', value=e.dst)
                    ),
                    UI.LayoutTableRow(
                        UI.Label(text='Filesystem: '),
                        UI.TextInput(name='fs', value=e.fs_type)
                    ),
                    UI.LayoutTableRow(
                        UI.Label(text='Options: '),
                        UI.TextInput(name='opts', value=opts)
                    )
              ),      
              UI.LayoutTable(
                    UI.LayoutTableRow(
                        UI.Checkbox(name='ro', checked=ro),
                        UI.Label(text='Read-only')
                    ),
                    UI.LayoutTableRow(
                        UI.Checkbox(name='bind', checked=bind),
                        UI.Label(text='Bind')
                    ),
                    UI.LayoutTableRow(
                        UI.Checkbox(name='loop', checked=loop),
                        UI.Label(text='Loop')
                    )
              ),
              UI.LayoutTable(
                    UI.LayoutTableRow(
                        UI.Label(text='Dump order: '),
                        UI.TextInput(name='dump_p', value=str(e.dump_p))
                    ),
                    UI.LayoutTableRow(
                        UI.Label(text='Fsck option: '),
                        UI.TextInput(name='fsck_p', value=str(e.fsck_p))
                    )
              )      
            )
        dlg = UI.DialogBox(
                t,
                title='Edit mount',
                id='dlgEdit'
              )
        return dlg
                    
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
        
class FSContent(ModuleContent):
    module = 'filesystems'
    path = __file__
    
    

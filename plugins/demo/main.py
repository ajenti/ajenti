from ajenti.ui import *
from ajenti.com import implements
from ajenti.app.api import ICategoryProvider
from ajenti.app.helpers import *


class DemoPlugin(CategoryPlugin):
    implements((ICategoryProvider, 90))

    text = 'Demo'
    description = 'All-new demo plugin'
    icon = '/dl/demo/icon.png'

    def on_session_start(self):
        self._labeltext = ''

    def get_ui(self):
        h = UI.HContainer(
               UI.Image(file='/dl/demo/bigicon.png'),
               UI.Spacer(width=10),
               UI.VContainer(
                   UI.Label(text='Demo plugin', size=5),
                   UI.Label(text=('Cool one, indeed'))
               )
            )

        p = UI.VContainer(
                h,
                UI.Spacer(height=20),
                UI.VContainer(
                    UI.Label(
                        text=self._labeltext,
                        size=4
                    ),
                    UI.Action(
                        text='Go!',
                        id='act-go',
                        icon='/dl/core/ui/icon-go.png',
                        description='Add some text'
                    )
                )
            )

        return p

    @event('action/click')
    def on_click(self, event, params, vars=None):
        if params[0] == 'act-go':
            self._labeltext += 'Kaboom! '


class DemoContent(ModuleContent):
    module = 'demo'
    path = __file__

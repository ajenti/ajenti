from ajenti.ui import *
from ajenti.com import implements
from ajenti.app.api import ICategoryProvider
from ajenti.app.helpers import *

class CronPlugin(CategoryPlugin):
    implements((ICategoryProvider, 90))

    text = 'Cron'
    description = 'Cron plugin'
    icon = '/dl/cron/icon.png'

    def on_session_start(self):
        self._labeltext = ''

    def get_ui(self):
        h = UI.HContainer(
               UI.Image(file='/dl/cron/bigicon.png'),
               UI.Spacer(width=10),
               UI.VContainer(
                   UI.Label(text='Cron plugin', size=5),
                   UI.Label(text=('Cool one, indeed'))
               )
            )
        text = "dsadas"
        p = UI.VContainer(
                h,
                UI.Spacer(height=20),
                UI.TextInputArea(
                                 text, "input", 20, 20, False),
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

class CronContent(ModuleContent):
    module = 'cron'
    path = __file__
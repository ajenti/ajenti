import aj
from jadi import component
from aj.plugins.augeas.api import AugeasEndpoint, Augeas
from aj.util import platform_select
from aj.plugins import PluginManager


@component(AugeasEndpoint)
class SupervisorEndpoint(AugeasEndpoint):
    id = 'supervisor'
    path = platform_select(
        debian='/etc/supervisor/supervisord.conf',
        default='/etc/supervisor.conf',
    )

    def get_augeas(self):
        return Augeas(
            modules=[{
                'name': 'Supervisor',
                'lens': 'Supervisor.lns',
                'incl': [
                    self.path,
                ]
            }],
            loadpath=PluginManager.get(aj.context).get_content_path('supervisor', ''),
        )

    def get_root_path(self):
        return '/files' + self.path

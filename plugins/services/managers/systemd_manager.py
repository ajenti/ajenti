import subprocess

from jadi import component
from aj.plugins.services.api import ServiceManager, Service, ServiceOperationError


@component(ServiceManager)
class SystemdServiceManager(ServiceManager):
    """
    Manager for systemd units.
    """

    id = 'systemd'
    name = 'systemd'

    @classmethod
    def __verify__(cls):
        """
        Test if systemd is installed.

        :return: Response from which.
        :rtype: bool
        """

        return subprocess.call(['which', 'systemctl']) == 0

    def __init__(self, context):
        pass

    def list(self, units=None):
        """
        Generator of all units service in systemd.

        :param units: List of services names
        :type units: list of strings
        :return: Service object
        :rtype: Service
        """

        if not units:
            units = [x.split()[0] for x in subprocess.check_output(['systemctl', 'list-unit-files', '--no-legend', '--no-pager', '-la']).decode().splitlines() if x]
            units = [x for x in units if x.endswith('.service') and '@.service' not in x]
            units = list(set(units))

        cmd = ['systemctl', 'show', '-o', 'json', '--full', '--all'] + units

        used_names = set()
        unit = {}
        for l in subprocess.check_output(cmd).decode().splitlines() + [None]:
            if not l:
                if len(unit) > 0:
                    svc = Service(self)
                    svc.id = unit['Id']
                    svc.name, _ = svc.id.rsplit('.', 1)

                    svc.name = svc.name.replace('\\x2d', '\x2d')
                    svc.running = unit['SubState'] == 'running'
                    svc.state = 'running' if svc.running else 'stopped'
                    svc.enabled = unit['UnitFileState'] == 'enabled'
                    svc.static = unit['UnitFileState'] == 'static'

                    if svc.name not in used_names:
                        yield svc

                    used_names.add(svc.name)
                unit = {}
            elif '=' in l:
                k, v = l.split('=', 1)
                unit[k] = v

    def get_service(self, _id):
        """
        Get informations from systemd for one specified service.

        :param _id: Service name
        :type _id: string
        :return: Service object
        :rtype: Service
        """

        for s in self.list(units=[_id]):
            return s

    def get_status(selfself, _id):
        """

        :param _id: Service name
        :type _id: string
        :return: Service status
        :rtype: string
        """

        return subprocess.check_output(['systemctl', 'status', _id, '--no-pager']).decode()

    def daemon_reload(self):
        """
        Basically restart a service.
        """

        subprocess.check_call(['systemctl', 'daemon-reload'], close_fds=True)

    def start(self, _id):
        """
        Basically start a service.

        :param _id: Service name
        :type _id: string
        """

        try:
            subprocess.check_call(['systemctl', 'start', _id], close_fds=True)
        except subprocess.CalledProcessError as e:
            raise ServiceOperationError(e)

    def stop(self, _id):
        """
        Basically stop a service.

        :param _id: Service name
        :type _id: string
        """

        try:
            subprocess.check_call(['systemctl', 'stop', _id], close_fds=True)
        except subprocess.CalledProcessError as e:
            raise ServiceOperationError(e)

    def restart(self, _id):
        """
        Basically restart a service.

        :param _id: Service name
        :type _id: string
        """

        try:
            subprocess.check_call(['systemctl', 'restart', _id], close_fds=True)
        except subprocess.CalledProcessError as e:
            raise ServiceOperationError(e)

    def kill(self, _id):
        """
        Basically kill a service.

        :param _id: Service name
        :type _id: string
        """

        try:
            subprocess.check_call(['systemctl', 'kill -s SIGKILL', _id], close_fds=True)
        except subprocess.CalledProcessError as e:
            raise ServiceOperationError(e)

    def disable(self, _id):
        """
        Basically disable a service.

        :param _id: Service name
        :type _id: string
        """

        try:
            self.stop(_id)
            subprocess.check_call(['systemctl', 'disable', _id], close_fds=True)
            self.daemon_reload()
        except subprocess.CalledProcessError as e:
            raise ServiceOperationError(e)

    def enable(self, _id):
        """
        Basically enable a service.

        :param _id: Service name
        :type _id: string
        """

        try:
            subprocess.check_call(['systemctl', 'enable', _id], close_fds=True)
            self.daemon_reload()
        except subprocess.CalledProcessError as e:
            raise ServiceOperationError(e)

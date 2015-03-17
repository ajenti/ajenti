import logging

from aj.plugins.core.api.tasks import Task
from aj.plugins.packages.api import PackageManager


class UpdateLists(Task):
    name = 'Update package lists'

    def __init__(self, context, manager_id=None):
        Task.__init__(self, context)
        for mgr in PackageManager.all(self.context):
            if mgr.id == manager_id:
                self.manager = mgr
                break
        else:
            logging.error('Package manager %s not found', manager_id)

    def run(self):
        self.manager.update_lists(self.report_progress)
        self.push('packages', 'refresh')

"""Custom Celery class for extensible_celery_worker."""


from celery import Celery


class ExtensibleCeleryWorkerCelery(Celery):
    """Custom Celery class to generate task names without ``.tasks.`` and with application name
    as prefix."""

    def gen_task_name(self, name, module):
        modules = module.split('.')
        # Remove 'tasks' at the end
        if modules[-1] == 'tasks':
            modules.pop()
        # Replace 'extensible_celery_worker' at the beginning with the app name
        if modules[0] == 'extensible_celery_worker':
            modules.pop(0)
        modules.insert(0, self.main)
        return super().gen_task_name(name, '.'.join(modules))

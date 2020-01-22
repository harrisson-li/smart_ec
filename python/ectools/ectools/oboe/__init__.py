import sys
from os.path import exists

from ectools.config import config, Cache


def _import_smart():
    """Only import smart one time then cache the status."""
    if getattr(Cache, 'not_import_smart', True):
        sys.path.insert(0, config.smart_repo)
        setattr(Cache, 'not_import_smart', False)


def set_smart_repo(repo_path):
    """
    Provide another smart repo instead use default value, required for Mac/Linux or when
    you cannot connect default smart repo. The default smart repo only support Windows system:

      - ``\\\\cns-qaauto5\Shared\git\smart``

    :param repo_path: e.g. ``/path/for/mac/linux``
    """
    if not exists(repo_path):
        raise ValueError('Invalid path: {}!'.format(repo_path))

    config.smart_repo = repo_path

    if getattr(Cache, 'not_import_smart', False):
        delattr(Cache, 'not_import_smart')

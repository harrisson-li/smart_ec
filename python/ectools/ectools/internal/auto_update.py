import os

from ectools.internal.objects import Configuration
from ectools.utility import no_ssl_requests, get_pkg_version, update_pkg, read_text, is_corp_net, ignore_error

VERSION_FILE = Configuration.version_file
VERSION_URL = Configuration.version_url
NAME = 'ectools'


def get_latest_version():
    if os.name == 'nt':  # access file on windows will be faster
        return read_text(VERSION_FILE)
    else:
        return no_ssl_requests().get(VERSION_URL).text


@ignore_error
def check_update(install=True):
    if not is_corp_net():
        return

    latest_version = get_latest_version()
    installed_version = get_pkg_version(NAME)

    if latest_version != installed_version:

        if install:
            update_pkg(NAME)
        else:
            print('New version of {} is available, {}=>{}'.
                  format(NAME, installed_version, latest_version))

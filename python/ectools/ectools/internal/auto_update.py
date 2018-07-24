import os

from ectools.utility import no_ssl_requests, get_pkg_version, update_pkg, read_text

VERSION_FILE = r"\\cns-qaauto5\Shared\Automation\ectools.txt"
VERSION_URL = 'http://cns-qaauto5/view/shared/automation/ectools.txt'
NAME = 'ectools'


def get_latest_version():
    if os.name == 'nt':  # access file on windows will be faster
        return read_text(VERSION_FILE)
    else:
        return no_ssl_requests().get(VERSION_URL).text


def check_update(install=True):
    latest_version = get_latest_version()
    installed_version = get_pkg_version(NAME)

    if latest_version != installed_version:

        if install:
            update_pkg(NAME)
        else:
            print('New version of {} is available, {}=>{}'.
                  format(NAME, installed_version, latest_version))

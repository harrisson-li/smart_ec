"""
Use build.py to create ectools automatically.

Supported options:
    -h  show help info.
    -t  run unit tests.
    -p  generate and upload package.
    -d  generate and upload document.

Examples:
    python build.py
        - run all steps, run tests, generate and upload package, document.
    python build.py -t
        - run unit tests only.
    python build.py -t -p
        - run unit tests and generate + upload package.
"""

import fileinput
import glob
import os
import re
import shutil
import sys
from os.path import dirname, join, exists, abspath

project_dir = abspath(dirname(__file__))
output_dir = join(project_dir, 'output')
package_dir = join(project_dir, 'dist')
test_result_dir = join(output_dir, 'results')
unit_test_dir = join(project_dir, 'ectools/_tests')
pypi_dir = r"\\cns-etnexus\pypi\ectools"
setup_py = join(project_dir, 'setup.py')
doc_dir = join(project_dir, 'doc')
doc_cmd = join(doc_dir, 'make.bat')
doc_server = join(pypi_dir, 'doc')


def prepare():
    if not exists(output_dir):
        os.makedirs(output_dir)

    shutil.rmtree(test_result_dir, ignore_errors=True)
    shutil.rmtree(package_dir, ignore_errors=True)
    os.makedirs(test_result_dir)


def unit_tests():
    test_modules = [x for x in os.listdir(unit_test_dir) if x != '__init__.py']

    for test_module in test_modules:
        full_path = join(unit_test_dir, test_module)
        result_name = full_path.replace(unit_test_dir, "").replace('\\', '_')
        result_path = join(test_result_dir, result_name + '.xml')

        cmd = 'pytest "{}" --verbose --junitxml="{}"'.format(full_path, result_path)
        os.system(cmd)


def update_version(new_version):
    def update(match):
        if int(match.group(2)) == 0 and new_version != 1:  # major version reset, no need to update
            return ''.join(match.groups())

        else:
            return '{}{}"'.format(match.group(1), new_version)

    for line in fileinput.input(setup_py, inplace=True):
        if 'version=' in line:
            line = re.sub(r'(.*\.)(\d+)(")', update, line)

        sys.stdout.write(line)


def make_package():
    assert exists(pypi_dir), 'Cannot access to pypi server: {}'.format(pypi_dir)

    if len(os.listdir(pypi_dir)):
        latest_build = max(glob.iglob(pypi_dir + '/*.gz'), key=os.path.getctime)
        latest_version = re.search(r'-\d+\.\d+\.(\d+)\.tar\.gz', latest_build).group(1)
        update_version(int(latest_version) + 1)

    os.system('python "{}" sdist'.format(setup_py))


def upload_package():
    os.chdir(project_dir)
    for package in os.listdir(package_dir):
        src = join(package_dir, package)
        dst = join(pypi_dir, package)
        shutil.copy(src, dst)


def make_doc():
    cmd = "{} html".format(doc_cmd)
    os.system(cmd)


def upload_doc():
    shutil.rmtree(doc_server)
    src = join(doc_dir, 'build', 'html')
    shutil.copytree(src, doc_server)


if __name__ == '__main__':
    args = sys.argv
    prepare()

    if len(args) == 1:
        unit_tests()
        make_package()
        upload_package()

    else:
        if '-t' in args:
            unit_tests()

        if '-p' in args:
            make_package()
            upload_package()

        if '-d' in args:
            make_doc()
            upload_doc()

        if '-h' in args:
            print(__doc__)

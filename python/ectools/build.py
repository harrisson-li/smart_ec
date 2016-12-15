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


def prepare():
    if not exists(output_dir):
        os.makedirs(output_dir)

    shutil.rmtree(test_result_dir, ignore_errors=True)
    shutil.rmtree(package_dir, ignore_errors=True)
    os.makedirs(test_result_dir)


def unit_tests():
    test_modules = [m for m in os.listdir(unit_test_dir) if m == 'config_tests.py']

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


if __name__ == '__main__':
    prepare()
    unit_tests()
    make_package()
    upload_package()

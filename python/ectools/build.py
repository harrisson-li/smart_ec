import os
import sys
from os.path import dirname, join, exists, abspath
import shutil

project_dir = dirname(__file__)
output_dir = join(project_dir, 'output')
test_result_dir = join(output_dir, 'results')
unit_test_dir = join(project_dir, 'ectools/_unittests')


def prepare():
    os.makedirs(output_dir, exist_ok=True)
    shutil.rmtree(test_result_dir, ignore_errors=True)
    os.makedirs(test_result_dir)


def unit_tests():
    test_modules = [m for m in os.listdir(unit_test_dir) if m == 'config_tests.py']
    for test_module in test_modules:
        full_path = join(unit_test_dir, test_module)
        result_name = full_path.replace(unit_test_dir, "").replace('\\', '_')
        result_path = join(test_result_dir, result_name + '.xml')

        cmd = 'pytest "{}" --verbose --junitxml="{}"'.format(full_path, result_path)
        os.system(cmd)


if __name__ == '__main__':
    prepare()
    unit_tests()

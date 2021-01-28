import platform

from setuptools import setup, find_packages


def main():
    if platform.system() == 'Linux':
        pymssql_pack = 'pymssql-linux'
    else:
        pymssql_pack = 'pymssql'    # Mac - Darwin, Windows - Windows

    setup(
        name="ectools",
        description="Toolbox from EFEC QA team.",
        long_description="Library to help with EFEC testing, such as create test account, submit score, get tokens.",
        version="1.9.12",
        author="Toby Qin",
        author_email="toby.qin@ef.com",
        url="https://confluence.eflabs.cn/display/SMart/ectools+-+Introduction",
        packages=find_packages(exclude=['tests', 'tests.*']),
        package_data={"ectools": ["data/*.csv", "data/*.sql"]},
        install_requires=[
            'requests',
            'selenium',
            'assertpy',
            'arrow',
            'bs4',
            'lxml',
            pymssql_pack,
            'numpy',
            'xmltodict'
        ],
        zip_safe=False,
    )


if __name__ == "__main__":
    main()

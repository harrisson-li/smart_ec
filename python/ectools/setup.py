from setuptools import setup, find_packages


def main():
    setup(
        name="ectools",
        description="Toolbox from EFEC QA team.",
        long_description="library to help with EFEC testing, such as create test account, submit score, get tokens.",
        version="1.5.14",
        author="Toby Qin",
        author_email="toby.qin@ef.com",
        url="https://confluence.englishtown.cn/display/SMart/ectools+-+Introduction",
        packages=find_packages(exclude=['tests', 'tests.*']),
        package_data={"ectools": ["data/*.csv", "data/*.sql"]},
        install_requires=[
            'requests',
            'selenium',
            'pymssql',
            'assertpy',
            'arrow',
            'bs4',
            'lxml'
        ],
        zip_safe=False,
    )


if __name__ == "__main__":
    main()

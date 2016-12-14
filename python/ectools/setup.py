from setuptools import setup


def main():
    setup(
        name="ectools",
        description="Toolbox from EFEC QA team.",
        long_description="library to help with EFEC testing, such as create test account, submit score, get tokens.",
        version="0.0.1",
        author="Toby Qin",
        author_email="toby.qin@ef.com",
        url="http://todo",
        packages=["ectools"],
        package_data={"ectools": ["data/*.csv"]},
        install_requires=[
            'requests',
            'selenium',            
			'pyodbc'
        ],
        zip_safe=False,
    )


if __name__ == "__main__":
    main()

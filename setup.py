import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="gitlab-attendant",
    version="0.0.1",
    author="Stuart McColl",
    author_email="it@stuartmccoll.co.uk",
    description="A GitLab bot that tidies and attends to repositories",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords="gitlab bot python",
    url="https://github.com/stuartmccoll/gitlab-attendant",
    entry_points={
        "console_scripts": ["gitlab-attendant=gitlab_attendant.main:main"]
    },
    packages=setuptools.find_packages(),
    install_requires=["requests", "pytz", "python-dateutil", "schedule==0.5.0"],
    tests_require=["unittest", "mock", "pytz"],
    classifiers=(
        "Environment :: Console",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)

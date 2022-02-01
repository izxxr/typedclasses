from setuptools import setup


with open("README.MD", "r") as f:
    LONG_DESCRIPTION = f.read()

VERSION = "0.0.1"
GITHUB = "https://github.com/nerdguyahmad/typedclasses"
LICENSE = "MIT"
REQUIREMENTS = []
PACKAGES = ["typedclasses"]

setup(
    name="typedclasses",
    author="nerdguyahmad",
    version=VERSION,
    license=LICENSE,
    url=GITHUB,
    project_urls={
        "Documentation": GITHUB + "/wiki",
        "Issue tracker": GITHUB + "/issues",
    },
    description='Python classes with types validation at runtime.',
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    include_package_data=True,
    install_requires=REQUIREMENTS,
    packages=PACKAGES,
    python_requires='>=3.8.0',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
        'Typing :: Typed',
    ]
)
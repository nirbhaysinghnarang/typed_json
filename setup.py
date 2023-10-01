from setuptools import setup, find_packages
setup(
    name="json-typed",
    version="0.1.1",
    packages=find_packages(),
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    include_package_data=True,
    install_requires=[
        "typing",
        "inspect",
        "collections",
        "json"
    ],
)

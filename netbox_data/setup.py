from setuptools import find_packages, setup

setup(
    name='netbox_data',
    version='0.1',
    description='A NetBox plugin that gets Netbox data.',
    install_requires=[],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
)
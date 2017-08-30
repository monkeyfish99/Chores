from setuptools import setup

setup(
    name='chores',
    packages=['chores'],
    include_package_data=True,
    install_requires=[
        'flask', 'flask-bcrypt',
    ],
)

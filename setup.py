from setuptools import setup

setup(
    name='spyder',
    version='0.1',
    entry_points={
        'console_scripts': ['spyder=spyder.__main__:main']
    },
    packages=['spyder'],
    url='',
    license='',
    author='Matt Dumford',
    author_email='mdumford99@gmail.com',
    description=''
)

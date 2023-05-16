from setuptools import setup
setup(
    name='search',
    version='0.0.1',
    entry_points={
        'console_scripts': [
            'search=search:run',
            'searchconfig=search:config'
        ]
    }
)
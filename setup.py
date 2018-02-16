from setuptools import setup, find_packages

setup(
    name='j2render',
    version='0.0.1',
    description='Render Jinja2 templates with parameters from a layered parameter tree',
    author='Aleksandra Fedorova',
    author_email='alpha@bookwar.info',
    classifiers=[
        'Development Status :: 3 - Alpha',
    ],

    packages=find_packages(exclude=['j2render']),

    entry_points={
        'console_scripts': [
            'j2render=j2render:main',
        ],
    },
)

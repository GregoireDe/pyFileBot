from setuptools import find_packages, setup

import pyfilebot

requires = [
    'click',
    'tvdbsimple',
    'guessit',
    'imdbpy',
]

setup(
    name=pyfilebot.__title__,
    version=pyfilebot.__version__,
    description='Rename tv show and movie files',
    #long_description=long_desc(),
    author=pyfilebot.__author__,
    author_email='pyfilebot@havi.fr',
    url='https://github.com/GregoireDelorme/pyFileBot',
    license='MIT',
    packages=find_packages(exclude=['docs', 'tests']),
    entry_points={'console_scripts': ['tvr=tvrenamr.cli.core:rename']},
    install_requires=requires,
    classifiers=[
        'Development Status :: 6 - Mature',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Topic :: Utilities',
    ],
)
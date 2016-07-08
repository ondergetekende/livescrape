from setuptools import setup

setup(
    name='livescrape',
    version='0.9.8',
    url='https://github.com/ondergetekende/python-livescrape',
    description='A toolkit to build pythonic web scraper libraries',
    author='Koert van der Veer',
    author_email='koert@ondergetekende.nl',
    py_modules=["livescrape"],
    install_requires=["lxml", "requests", "cssselect", "six"],
    classifiers=[
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 2.7',
    ],
)

from setuptools import setup

setup(
    name='relation_extraction_utils',
    version='0.0.2',
    packages=['relation_extraction_utils', 'relation_extraction_utils.internal'],
    url='https://github.com/comp-aspects-of-appl-linguistics/relation_extraction_utils',
    license='GPLv3',
    author='Or, Shachar, Jonathan',
    author_email='',
    description='Various utilities for processing and analyzing relation extraction related data',
    install_requires=[
        'stanfordnlp', 'nltk', 'pandas', 'networkx', 'spacy'
    ],
    scripts=['bin/parse_ud']
)

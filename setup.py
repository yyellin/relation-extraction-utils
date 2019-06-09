from setuptools import setup

setup(
    name='relation_extraction_utils',
    version='0.1.0',
    packages=['relation_extraction_utils', 'relation_extraction_utils.internal'],
    url='https://github.com/comp-aspects-of-appl-linguistics/relation_extraction_utils',
    license='GPLv3',
    author='Or, Shachar, Jonathan',
    author_email='',
    description='Various utilities for processing and analyzing relation extraction related data',
    install_requires=[
        'stanfordnlp', 'nltk', 'pandas', 'networkx', 'spacy'
    ],
    scripts=[
        'bin/tac_to_csv',
        'bin/parse_ud',
        'bin/parse_ner',
        'bin/parse_pss',
        'bin/parse_ucca',
        'bin/identify_relations']
)

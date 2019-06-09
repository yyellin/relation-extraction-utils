from setuptools import setup

setup(
    name='relation_extraction_utils',
    version='0.0.3',
    packages=['relation_extraction_utils', 'relation_extraction_utils.internal'],
    url='https://github.com/comp-aspects-of-appl-linguistics/relation_extraction_utils',
    license='GPLv3',
    author='Or, Shachar, Jonathan',
    author_email='',
    description='Various utilities for processing and analyzing relation extraction related data',
    install_requires=[
        'stanfordnlp', 'nltk', 'pandas', 'networkx', 'spacy'
    ],
    dependency_links=[
        'git+https://github.com/danielhers/ucca.git@master',
        'git+https://github.com/OfirArviv/tupa.git@elmo_weighted_w_special_tokens_to_lstm_mlp'
    ],
    scripts=['bin/tac_to_csv', 'bin/parse_ud', 'bin/parse_ner', 'bin/parse_pss', 'bin/identify_relations']
)

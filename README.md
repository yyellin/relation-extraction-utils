# relation-extraction-utils: Utility packages for relation extraction

The relation-extraction-utils project is an assembly of Python 3 packages used by Or, Shachar and Jonathan in support of their graduate work in the field of rules based systems for relation extraction.



## Modules

| Modules | Purpose |
|---|---|
| generate_csv_file | Given a TAC Relation Extraction Dataset in json format, and a given relation (e.g. 'per:employee_of'), the purpose of this module is to provide functionality for extracting all sentences where the relation is tagged in the dataset, parsing the relevant sentence into a Universal Dependency  v2 trees (using [stanfordnlp](<https://stanfordnlp.github.io/stanfordnlp/>)), producing a comma delimited file in which the researcher is then expected to identify **trigger words** |
| display_path_stats | Receives a pre-populated comma delimited file containing sentences from the TAC Relation Extraction Dataset identified as containing a given relationship, and calculates paths from trigger word to relation entities, and between the entities themselves |
| identify_false_positives |  |

## Setup

relation-extraction-utils supports Python 3.6 or later; you can also install from source of this git repository by running:
```bash
pip install -U git+https://github.com/comp-aspects-of-appl-linguistics/relation_extraction_utils.git
```

## License

relation-extraction-utils is released under GPLv3.

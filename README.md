# relation-extraction-utils: Utility packages for relation extraction

The relation-extraction-utils project is an assembly of Python 3 packages used by Or, Shachar and Jonathan in support of their graduate work in the field of rules based systems for relation extraction.

## Packages

| Package | Purpose |
|---|---|
| prepare_for_trigger_identification | Defines the 'generate_cvs_file' module |
| count_trigger_paths | Defines the 'PathStats' class, which receives a pre-populated CVS file containing sentences from the TAC Relation Extraction Dataset identified as containing a given relationship, and calculates paths from trigger word to relation entities, and between the entities themselves |
|  |  |

## Setup

relation-extraction-utils supports Python 3.6 or later; you can also install from source of this git repository by running:
```bash
pip install -U git+https://github.com/comp-aspects-of-appl-linguistics/relation_extraction_utils.git
```

## License

relation-extraction-utils is released under GPLv3.

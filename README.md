# relation-extraction-utils: Syntactic & semantic based patterns for relation extraction, with supporting software

## Introduction

The relation-extraction-utils project contains an assembly of Python 3 packages used by Or, Shachar and Jonathan in support of their graduate lab work in the field of rules based systems for relation extraction.

The aim of the lab is to assess whether it is possible to improve on the results of traditional pattern based approaches for identifying relations between two entities by considering patterns that stem from semantical structure of sentences, as expressed by [UCCA](http://www.cs.huji.ac.il/~oabend/ucca.htm) .

We relied on the [TAC Relation Extraction Dataset](https://catalog.ldc.upenn.edu/LDC2018T24 )  as our input. This dataset contains a total of 106,264 entries each representing a single sentences. Each entry contains identification of two entities and their TAC KBP relation, or no relation at all. Additionally, each entry contains Standford NLP based parts-of-speech tagging, NER tagging and dependency tree, however we did not utilize this data. The sentences are divided into sets of Train, Dev and Test.  

For the purpose of our study, we focused on the 'org:founded_by' relationship - with 124 appearances in the Train set and 76 appearances in the Dev set. 

## Method

We focus on relations that arise from individual sentences, and assume that a reader's ability to infer the existence of a relationship between two entities is generally contingent on the existence of  "trigger word".  We designed and implemented a software based *pipeline* for both pattern extraction and pattern application, with the former requiring minimal human intervention, and the latter requiring no human intervention at all. 

The patterns themselves are based on the concept of a *path* between tokens in the sentence; specifically: a pattern consists of an expression of the path between the first entity and the trigger word, and then from the trigger word to the second entity. 

The heart of this project is in the benefit of the leveraging of two sentence parsing paradigms in order to express the path between tokens:

##### [Universal Dependencies v2](https://en.wikipedia.org/wiki/Universal_Dependencies) 

"The UD annotation scheme produces syntactic analyses of sentences in terms of the dependencies of dependency grammar. Each dependency is characterized in terms of a syntactic function, which is shown using a label on the dependency edge.

[^wikipedia]: asdasd

" 

##### [UCCA](<http://www.cs.huji.ac.il/~oabend/ucca.html>)



The pipeline process is repeated for two classes of sentence structure: for 



### Pattern Extraction

P

![](C:\Users\jyellin\Desktop\Relation-Extraction.png)





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

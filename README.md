# relation-extraction-utils: improving the results of relation extraction with syntactic based patterns by leveraging semantic based patterns (with supporting software)

## Introduction

The relation-extraction-utils project contains an assembly of Python 3 packages used by Or, Shachar and Jonathan in support of their graduate lab work in the field of rules based systems for relation extraction, under the guidance of [Dr. Omri Abend](http://www.cs.huji.ac.il/~oabend/).

The aim of the lab is to assess whether it is possible to improve on the results of traditional pattern based approaches for identifying relations between two entities by considering patterns that stem from semantical structure of sentences, as expressed by [UCCA](http://www.cs.huji.ac.il/~oabend/ucca.htm) .

We relied on the [TAC Relation Extraction Dataset](https://catalog.ldc.upenn.edu/LDC2018T24 )  as our input. This dataset contains a total of 106,264 entries each representing a single sentences. Each entry contains identification of two entities and their TAC KBP relation, or no relation at all. Additionally, each entry contains Standford NLP based parts-of-speech tagging, NER tagging and dependency tree, however we did not utilize this data. The sentences are divided into sets of Train, Dev and Test.  

For the purpose of our study, we focused on the 'org:founded_by' relationship - with 124 appearances in the Train set and 76 appearances in the Dev set. 

## Method

We focus on relations that arise from individual sentences, and assume that the ability of a human reader or listener to infer the existence of a relationship between two entities is generally contingent on the existence of  "trigger word".  We designed and implemented a software based *pipeline* for both pattern extraction and pattern application, with the former requiring minimal human intervention, and the latter requiring no human intervention at all. 

The patterns themselves are based on the concept of a *path* between tokens in the sentence; specifically, a pattern consists of an expression of the path between the first entity and the trigger word, and then from the trigger word to the second entity. 

The heart of this project is a technique for capturing a path between tokens using a sentences dependency structures. To this end we leverage two sentence dependency structures paradigms - the syntactic UDv2 and the semantic UCCA. 

### [Universal Dependencies v2](<https://universaldependencies.org/>) 

"The UD annotation scheme produces syntactic analyses of sentences in terms of the dependencies of dependency grammar. Each dependency is characterized in terms of a syntactic function, which is shown using a label on the dependency edge." (from [Wikipedia article on Universal Dependencies](https://universaldependencies.org/)). 

Version 2 of Universal Dependencies represents an advancement of the syntactic dependencies, and it is the version used in this work. At the time of writing the only freely available software package that supports the parsing of a sentence into v2 of UD that we were able to identify is [StanfordNLP: A Python NLP Library for Many Human Languages](<https://github.com/stanfordnlp/stanfordnlp>). The well known [Java based NLP library from Standford](<https://github.com/stanfordnlp/CoreNLP>) is still oriented to v1 of UD.

To explain how the paths are reflected as a pattern, we consider the sentence "Access Industries, a privately held company *founded* in 1986 by Len Blavatnik, has a diverse portfolio of investments in industry, real estate, media and telecommunications" (id: e7798385822df5ab337e, docid: APW_ENG_20090612.0855). It contains an *org:founded_by* relationship between the organization *'Access Industries'* and the person *'Len Blavatnik'*; the trigger word we identified in this case is the word *'founded'*.

We consider the dependency structure of the sentence:

![UD v2 dependency tree](images-for-readme/udv2.png)

Entity one is *'Access Industries'*, entity two is *'Len Blavatnik'* and the trigger word us *'founded'* - the path from entity one to the trigger word (which we define to be the shortest possible path) follows this trail: from the token *'Industries'* in the direction of its *appos* dependency child, the token *'company'*, and then from the token *'company'* to its *acl* dependency child *'founded'*. We capture this path as **!appos !acl** where the '!' represents a move from parent to child; a step from child to parent would be represented with the '^' (so for example, the path from *'founded'* back to *'Industries'* would be represented with the string **^acl ^appos**). The second part of the pattern represents the path from the tojen *'founded'* to the token *'Len'*. Using the same system we get **!obl**. We capture both parts of the path by concatenating them, using the symbol **><** to represent the trigger word, yielding the full path of **!appos !acl >< !obl**.

### [UCCA](<http://www.cs.huji.ac.il/~oabend/ucca.html>)

While UD describes sentence structure in syntactical terms, UCCA (Universal Conceptual Cognitive Annotation) is a semantical approach to grammatical representations.  We used a specific branch of the [Transition-based UCCA Parser](https://github.com/OfirArviv/tupa) for our work, in conjunction with the elmo model. More on this in section XX.

We consider the UCCA structure of the sentence we presented above:

![UCCA ](images-for-readme/ucca.png)

Now we need to capture the shortest path from token #0.1 *'Access'* to token #0.8 *'founded'*: starting from #0.1's parent, #1.7, against the direction of the dependency to #1.3, and then from #1.3, with the direction of the dependency, to #1.10, #1.24 and finally #1.33. We express both the type of link and the direction we flow in the path to give us **^E !E !E !P**. In the same vein, the path from the trigger word's parent #1.33 to entity two's parent is **^P !A !C**. Considering both legs of the path, and symbolizing the trigger word with **><**  we get the pattern **^E !E !E !P >< ^P !A !C** for the entire path.

## Pipeline

Armed with the method described above we implemented ....

WORK IN PROGRESS

### Pattern Extraction



![](images-for-readme/path-identification.png)

### 



## Code

### Modules

| Modules | Purpose |
|---|---|
| generate_csv_file | Given a TAC Relation Extraction Dataset in json format, and a given relation (e.g. 'per:employee_of'), the purpose of this module is to provide functionality for extracting all sentences where the relation is tagged in the dataset, parsing the relevant sentence into a Universal Dependency  v2 trees (using [stanfordnlp](<https://stanfordnlp.github.io/stanfordnlp/>)), producing a comma delimited file in which the researcher is then expected to identify **trigger words** |
| display_path_stats | Receives a pre-populated comma delimited file containing sentences from the TAC Relation Extraction Dataset identified as containing a given relationship, and calculates paths from trigger word to relation entities, and between the entities themselves |
| identify_false_positives |  |

### Setup

relation-extraction-utils supports Python 3.6 or later; you can also install from source of this git repository by running:
```bash
pip install -U git+https://github.com/comp-aspects-of-appl-linguistics/relation_extraction_utils.git
```

### License

relation-extraction-utils is released under GPLv3.

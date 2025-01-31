---
title:  "Working with RDF Graph Databases in Python"
author: Leo Rudczenko
categories:
  - Software Engineering
tags:
  - python
  - graph
  - database
  - rdf
  - linked-data
---

BGS produces a number of linked datasets which are stored as RDF graph databases.
These include valuable lithology classification schemes - the [BGS Rock Classification Scheme](https://www.bgs.ac.uk/technologies/bgs-rock-classification-scheme/), and a simpler international equivalent the [CGI Simple Lithology](http://resource.geosciml.org/classifier/cgi/lithology) vocabulary which BGS helped develop.
We needed to parse some of this online RDF data
as we wanted to use the classifications in our new field data capture tool.
In particular, we wanted to traverse parent-child hierarchies,
so that we could use these to simplify colour attribution on a map of lithologies.
We chose to do this work in Python, as the tool was being developed as a Python
plugin for QGIS.

## How to parse a graph database in Python

To parse a graph database using Python, we are going to use the library
[`rdflib`](https://rdflib.readthedocs.io/en/stable/).
You can install this library using [`pip`](https://pip.pypa.io/en/stable/).

```
pip install rdflib
```

The file we are going to parse is a Turtle file (.ttl), which is a format for storing
triples. This files comes from the CGI Simple Lithology dataset, which you can find on GitHub
[here](https://raw.githubusercontent.com/CGI-IUGS/cgi-vocabs/9dfe161affbe91de4c25622a9c2cfab5aa65c642/vocabularies/geosciml/simplelithology.ttl).

Firstly, we have to create an empty graph using `rdflib`, and then use it to parse the given `ttl` file.

```python
import rdflib

uri = "https://raw.githubusercontent.com/CGI-IUGS/cgi-vocabs/9dfe161affbe91de4c25622a9c2cfab5aa65c642/vocabularies/geosciml/simplelithology.ttl"
# Create new graph
graph = rdflib.Graph()
# Parse the ttl file from the URI
graph.parse(uri, format="ttl")
```

Next, we are only going to be looking for `lithology` subjects from the graph database,
and we are only going to be looking for their `skos:prefLabel` and `skos:broader` predicates.
Therefore, we will define some URIs which we will use to filter our data.

```python
lithology_subject_prefix = "http://resource.geosciml.org/classifier/cgi/lithology/"
skos_pref_label_uri = rdflib.term.URIRef("http://www.w3.org/2004/02/skos/core#prefLabel")
skos_broader_uri = rdflib.term.URIRef("http://www.w3.org/2004/02/skos/core#broader")
```

We are now ready to start iterating over the `triples` within the graph. We will add this data to
a Python dictionary. When we iterate over the graph, we get a single predicate object
for a single subject. Therefore, we need to ensure we have the correct
structure to store all of the objects for each predicate of each subject.

```python
graph_dict = {}

for subject, predicate, object_ in graph:

    # Filter the triples where the subject URI starts with the lithology URI prefix
    if subject.startswith(lithology_subject_prefix):

        # Ensure the subject has a child dictionary to store predicates
        if subject not in graph_dict:
            graph_dict[subject] = {}

        # Ensure the predicate has a child list to store objects
        # We store the objects as lists because sometime there is more than 1 value
        # E.g. parent lithologies
        if predicate not in graph_dict[subject]:
            graph_dict[subject][predicate] = []

        # Add the new object to the dictionary
        graph_dict[subject][predicate].append(object_)

print(f"Found {len(graph_dict)} lithologies in the graph database!")
```

```
Found 265 lithologies in the graph database!
```

We now have a dictionary representation of our lithology classifications, from our graph database!
We can use this to find the data for `Rhyolite`, which was mentioned in our earlier example.

```python
# Import pretty printer to output the dictionary nicely
from pprint import pprint
rhyolite_uri = rdflib.term.URIRef('http://resource.geosciml.org/classifier/cgi/lithology/rhyolite')
pprint(graph_dict[rhyolite_uri])
```

```
{rdflib.term.URIRef('http://purl.org/dc/terms/provenance'): [rdflib.term.Literal('LeMaitre et al. 2002', lang='en')],
 rdflib.term.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'): [rdflib.term.URIRef('http://www.w3.org/2004/02/skos/core#Concept')],
 rdflib.term.URIRef('http://www.w3.org/2000/01/rdf-schema#isDefinedBy'): [rdflib.term.URIRef('http://resource.geosciml.org/classifierscheme/cgi/2016.01/simplelithology')],
 rdflib.term.URIRef('http://www.w3.org/2004/02/skos/core#altLabel'): [rdflib.term.Literal('liparita', lang='es'),
                                                                      rdflib.term.Literal('ryolit', lang='sv'),
                                                                      rdflib.term.Literal('Liparit', lang='de'),
                                                                      rdflib.term.Literal('liparite', lang='it'),
                                                                      rdflib.term.Literal('liparit', lang='ru'),
                                                                      rdflib.term.Literal('lipariitti', lang='fi')],
 rdflib.term.URIRef('http://www.w3.org/2004/02/skos/core#broader'): [rdflib.term.URIRef('http://resource.geosciml.org/classifier/cgi/lithology/rhyolitoid')],
 rdflib.term.URIRef('http://www.w3.org/2004/02/skos/core#definition'): [rdflib.term.Literal('rhyolitoid in which the ratio of plagioclase to total feldspar is between 0.1 and 0.65.', lang='en')],
 rdflib.term.URIRef('http://www.w3.org/2004/02/skos/core#exactMatch'): [rdflib.term.URIRef('http://inspire.ec.europa.eu/codelist/LithologyValue/rhyolite')],
 rdflib.term.URIRef('http://www.w3.org/2004/02/skos/core#example'): [rdflib.term.Literal('liparite', lang='en'),
                                                                     rdflib.term.Literal('rhyodacite', lang='en')],
 rdflib.term.URIRef('http://www.w3.org/2004/02/skos/core#inScheme'): [rdflib.term.URIRef('http://resource.geosciml.org/classifierscheme/cgi/2016.01/simplelithology')],
 rdflib.term.URIRef('http://www.w3.org/2004/02/skos/core#prefLabel'): [rdflib.term.Literal('silarIyU:lIt', lang='km'),
                                                                       rdflib.term.Literal('流纹岩', lang='zh'),
                                                                       rdflib.term.Literal('Rhyolith', lang='de'),
                                                                       rdflib.term.Literal('ryolit', lang='vi'),
                                                                       rdflib.term.Literal('流紋岩', lang='ja'),
                                                                       rdflib.term.Literal('유문암', lang='ko'),
                                                                       rdflib.term.Literal('riolit', lang='id'),
                                                                       rdflib.term.Literal('riolit', lang='ru'),
                                                                       rdflib.term.Literal('ryolit', lang='sv'),
                                                                       rdflib.term.Literal('¹ó\xadÄëÂºÄìª', lang='lo'),
                                                                       rdflib.term.Literal('rhyolite', lang='en'),
                                                                       rdflib.term.Literal('riolita', lang='es'),
                                                                       rdflib.term.Literal('ryoliitit', lang='fi'),
                                                                       rdflib.term.Literal('หินไรโอไรต์', lang='th'),
                                                                       rdflib.term.Literal('riolit', lang='ms'),
                                                                       rdflib.term.Literal('rhyolite', lang='fr'),
                                                                       rdflib.term.Literal('riolite', lang='it')]}
```

If we want to see its parents, we can access the object behind the predicate `skos:broader`.
Here we will also use the predicate `skos:prefLabel` to access the English name for the parents.

```python
broader_uris = graph_dict[rhyolite_uri][skos_broader_uri]
parents = []
for parent_uri in broader_uris:
    parent_labels = graph_dict[parent_uri][skos_pref_label_uri]
    # Get just the English label for each parent
    english_label = [label.toPython() for label in parent_labels if label.language == "en"][0]
    parents.append(english_label)

pprint(parents)
```

```
['rhyolitoid']
```

Finally, in this format of linked data, recursive functions are incredibly useful to traverse a graph
from one node to another. Or, in the case of `triples`, from one subject to another. Here, we will
use recursion to find the list of all parent lithology classifications above `Rhyolite`.

```python
def find_lithology_parents(
    graph_dict,
    target_lithology_uri,
    parent_labels = set(),
):
    """
    Find all of the parent lithology classifications above the given target_lithology_uri.
    A set of all parent labels is returned.
    We use a set because this ensures only unique values are stored within it.

    The argument 'parent_labels' can be ignored when calling this function,
    as it is used to start an empty set which is populated as the recursion iterates.
    """
    # If the target lithology has parents
    if skos_broader_uri in graph_dict[target_lithology_uri]:

        for parent_uri in graph_dict[target_lithology_uri][skos_broader_uri]:
            # Get the current parent English label
            current_parent_labels = graph_dict[parent_uri][skos_pref_label_uri]
            english_label = [label.toPython() for label in current_parent_labels if label.language == "en"][0]

            # Add the current parent to the set of all parents
            parent_labels.add(english_label)

            # Find the parents of the parent
            parent_parents = find_lithology_parents(graph_dict, parent_uri, parent_labels)
            # Add the parents of the parent to the set of all parents
            parent_labels = parent_labels.union(parent_parents)

    return parent_labels


rhyolite_parents = find_lithology_parents(graph_dict, rhyolite_uri)
pprint(rhyolite_parents)
```

```
{'acidic_igneous_material',
 'acidic_igneous_rock',
 'compound_material',
 'fine_grained_igneous_rock',
 'igneous_material',
 'igneous_rock',
 'rhyolitoid',
 'rock'}
```

## Alternative Solutions

It is worth noting that there are other ways of extracting data from a triplestore.
A common method includes [`SPARQL`](https://en.wikipedia.org/wiki/SPARQL),
which allows you to build queries on an RDF graph database resembling
[`SQL`](https://en.wikipedia.org/wiki/SQL).
You can even use `rdflib` to run `SPARQL` queries in Python.
More information on this from the `rdflib` documentation can be found
[here](https://rdflib.readthedocs.io/en/7.1.1/intro_to_sparql.html).

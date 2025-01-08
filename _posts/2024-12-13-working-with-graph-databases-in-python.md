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

## What are Graph Databases?

The logic behind a [Graph Database](https://en.wikipedia.org/wiki/Graph_database),
comes from graph theory in mathematics, where a network of nodes representing data are connected using edges.
This makes a graph database more flexible than a typical hierarchical database,
as new nodes can be added connected to any existing node, often without constraints.
This lack of constraints can be convientent, but it does mean that a user will need
additional context regarding the existing nodes before adding new ones, as the existing
data is unpredictable.
These constraints can be added using additional tools if required.
For example, when using
a [Resource Description Framework (RDF)](https://en.wikipedia.org/wiki/Resource_Description_Framework)
graph, you can add constraints
using [Shapes Constraint Language (SHACL)](https://en.wikipedia.org/wiki/SHACL).

In a graph database, everything is represented using URIs (Uniform Resource Identifier) or literals.
These URIs are what allows us to create new connections between nodes in the graph,
and even connections between multiple graphs.
For this to work, data is stored in `triples`. In a triple, we have:
- Subject: the row in a typical database, referring to one feature (URI)
- Predicate: the column in a typical database, referring to one attribute name (URI)
- Object: the value found at the given row/column, the attribute value (URI or literal)

The predicate URI should also be a subject itself, containing more triples that describe its definition.
This means that all of the context behind the data is described within the graph database,
an advantage which cannot be done in a relational database.

Let's apply this concept to a lithology example. If we want to represent Rhyolite's lithology classification
as an Igneous Rock in a triple, we could do the following:
- Subject: URI to Rhyolite
- Predicate: URI to Parent Definition
- Object: URI to Igneous Rock

The value from this data structure comes from the fact that in this example, we could find the predicates
of Igneous Rock using its own URI, and then continue to another subject after that.

The nature of `triples` also means that when you iterate over the `triples` in a
graph database, you get a single predicate object for a single subject at a time.
You do not get all of the predicates for a subject at once.
Therefore, you will likely want to parse the data into a different structure
to suit your requirements, depending on what you wish to do with the data.

It is important to note that because predicates are defined using a URI,
we can use pre-defined predicates from online `namespaces`.
In the example below, we will see many attributes from the online `skos` namespace,
such as `skos:prefLabel` which is essentially a human readable name,
and `skos:broader` which is a parent node.

You can find more information about the `skos` data model [here](https://www.w3.org/2009/08/skos-reference/skos.html).

## Why are we working with graph databases?

We started with hundreds of lithology classifcations which were going to be used in a
new Field Data Capture system, where users could input spatial lithology data.
We wanted to plot coloured points onto a map within the system,
so that a user could see all of their spatial lithology data visually, as this would allow them
to quickly make sense of their data.
However, applying hundreds of different colours to points on a map would make it very hard
to see differences between the colours, as they would be very similar.
Therefore, we wanted to select 50~ high level classifications,
so that every lithology could be attributed to one of these.
Finally, these 50~ classifications could be colour coded using colours which are more clearly different.

To do this, we decided to use the data from a graph database provided by the
[IUGS Commission for the Management and Application of Geoscience Information](https://cgi-iugs.org/),
called [CGI Geoscience Vocabularies](https://cgi.vocabs.ga.gov.au/).
This dataset contains information regarding lithology classifications and their relationships.
By parsing this data, we can produce a list of all parent lithology classifications,
for any given lithology classification.
In turn, this would help us identify our 50~ high level classifications.

## How to parse a graph database in Python

Now that we have an overview of graph databases, we will parse one using Python!
To do this, we are going to use the library [`rdflib`](https://rdflib.readthedocs.io/en/stable/).
You can install this library using [`pip`](https://pip.pypa.io/en/stable/).

```
pip install rdflib
```

The file we are going to parse is a Turtle file (.ttl), which is a format for storing
graph databases. You can find the file in this example on GitHub [here](https://raw.githubusercontent.com/CGI-IUGS/cgi-vocabs/9dfe161affbe91de4c25622a9c2cfab5aa65c642/vocabularies/geosciml/simplelithology.ttl).
This graph database contains information about lithology classifications.

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
lithology__subject_prefix = "http://resource.geosciml.org/classifier/cgi/lithology/"
skos_pref_label_uri = rdflib.term.URIRef("http://www.w3.org/2004/02/skos/core#prefLabel")
skos_broader_uri = rdflib.term.URIRef("http://www.w3.org/2004/02/skos/core#broader")
```

We are now ready to start iterating over the `triples` within the graph. We will add this data to
a Python dictionary. Remember, when we iterate over the graph, we get a single predicate object
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

print(f"Found {len(graph_dict)} lithologies in triplestore!")
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
    # Get just the English label for the parent
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
    target_lithology,
    parents = set(),
):
    """
    Find all of the parent lithology classifications above the given target_lithology.
    A set of all parents is returned.
    We use a set because this ensures only unique values are stored within it.

    The argument 'parents' can be ignored when calling this function,
    as it is used to start an empty set which is populated as the recursion iterates.
    """
    # If the target_lithology has parents
    if skos_broader_uri in graph_dict[target_lithology]:

        for parent_uri in graph_dict[target_lithology][skos_broader_uri]:
            # Get the current parent English label
            current_parent_labels = graph_dict[parent_uri][skos_pref_label_uri]
            english_label = [label.toPython() for label in current_parent_labels if label.language == "en"][0]

            # Add the current parent to the set of all parents
            parents.add(english_label)

            # Find the parents of the parent
            parent_parents = find_lithology_parents(graph_dict, parent_uri, parents)
            # Add the parents of the parent to the set of all parents
            parents = parents.union(parent_parents)

    return parents


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

It is worth noting that there are other ways of parsing data within a graph database.
A common method includes [`SPARQL`](https://www.w3.org/TR/sparql11-overview/),
which allows you to build graph database queries resmebling
[`SQL`](https://learn.microsoft.com/en-us/sql/t-sql/queries/select-transact-sql?view=sql-server-ver16).
You can even use `rdflib` to run `SPARQL` queries in Python.
More information on this from the `rdflib` documentation can be found
[here](https://rdflib.readthedocs.io/en/7.1.1/intro_to_sparql.html).

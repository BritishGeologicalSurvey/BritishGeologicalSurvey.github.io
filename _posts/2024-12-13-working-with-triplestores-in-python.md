---
title:  "Working with Triplestores in Python"
author: Leo Rudczenko
categories:
  - Software Engineering
tags:
  - python
  - triplestores
  - database
  - rdf
  - linked-data
---

## What are triplestores?

Triplestores are a type of graph database, as their data structure can be represented using graphs.
The data in them does not have to conform to typical hierarchical database relationships.
Instead, they can have relationship links which cross over and go back and forth, just like a graph.
This allows us to represent more complex data structures, such as lithology classifications,
where the relationships are intertwined like a spider's web.

In a triplestore, everything is represented using URIs (Uniform Resource Identifier).
The nodes on the graph, the attribute names, and the attribute values are all URIs.
This is what creates the relationships, as everything is linked.
For this to work, data is stored in `triples`. In a triple, we have:
- Subject: the row in a typical database, referring to one feature
- Predicate: the column in a typical database, referring to one attribute name
- Object: the value found at the given row/column, the attribute value

Let's apply this concept to a lithology example. If we want to represent Rhyolite's lithology classification
as an Igneous Rock in a triple, we could do the following:
- Subject: URI to Rhyolite
- Predicate: URI to Lithology classification
- Object: URI to Igneous Rock

The value from this data structure comes from the fact that in this example, we could find the predicates
(attributes) of Igneous Rock using its own URI, and then continue to another node after that.
This also means that data which would usually be stored in different tables, can be stored within
a single triple store, as every subject has its own URI providing its definition.

The nature of `triples` also means that when you iterate over the `triples` in a
triplestore, you get a single predicate object for a single subject (a single
attribute value for a single row) at a time. You do not get all of the predicates (attributes) for
a subject (row) at once. Therefore, you will likely want to parse the data into a different structure
to suit your requirements, depending on what you wish to do with the data.

It is important to note that because predicates (attributes) are defined using a URI,
we can use pre-defined predicates (attributes) from online `namespaces`.
In the example below, we will see many attributes from the online `skos` namespace,
such as `skos:definition` which is essentially a description,
and `skos:narrower` which is a list of child nodes.

You can find more information about the `skos` data model [here](https://www.w3.org/2009/08/skos-reference/skos.html).

## How to parse a triplestore in Python

Now that we have an overview of triplestores, we will parse one using Python!
To do this, we are going to use the library `rdflib`, which can be installed using `pip`:

```
pip install rdflib
```

The file we are going to parse is a Turtle file (.ttl), which is a format for storing
triplestores. You can find the file in this example on GitHub [here](https://raw.githubusercontent.com/CGI-IUGS/cgi-vocabs/9dfe161affbe91de4c25622a9c2cfab5aa65c642/vocabularies/geosciml/simplelithology.ttl).
This triplestore contains information about lithology classifications.

Firstly, we have to create an empty graph using `rdflib`, and then use it to parse the given `ttl` file.

```python
from rdflib import Graph

uri = "https://raw.githubusercontent.com/CGI-IUGS/cgi-vocabs/9dfe161affbe91de4c25622a9c2cfab5aa65c642/vocabularies/geosciml/simplelithology.ttl"
# Create new graph
graph = Graph()
# Parse the ttl file from the URI
graph.parse(uri, format="ttl")
```

Now in this example, we are only going to be reading the `skos` namespace predicates (attributes).
Therefore, we need to get the URI for the `skos` namespace,
so we can use it to filter the `triples`.

```python
# Get the skos namespace URI from the list of namespaces in the ttl file
# namespaces are tuples with 2 items, [namespace string identifer, namespace URI]
skos_namespace = [
    namespace[1] 
    for namespace in graph.namespaces()
    if namespace[0] == "skos"
][0]
```

Next, we are only going to be looking for `lithology` subjects from the triplestore.
Therefore, we will define a URI to further filter the `triples`.

```python
# Subject prefix
lithology_prefix = "http://resource.geosciml.org/classifier/cgi/lithology/"
```

We are now ready to start iterating over the `triples` within the graph. We will add this data to
a Python dictionary. Remember, when we iterate over the graph, we get a single predicate object
(attribute value) for a single subject (row). Therefore, we need to ensure we have the correct
structure to store all of the objects (values) for each predicate (attribute) of each subject (row).

```python
graph_dict = {}

# Can be thought of like database structure: row, column, value
for subject, predicate, object_ in graph:

    # Filter the triples where
    # the subject URI starts with the lithology URI prefix
    # and the predicate URI starts with the skos namespace
    if subject.startswith(lithology_prefix) and predicate.startswith(skos_namespace):

        # Get the subject name by removing the lithology URI prefix
        subject_name = subject.removeprefix(lithology_prefix)

        # Get the predicate name by removing the namespace prefix from the URI
        predicate_name = predicate.removeprefix(skos_namespace)

        # Ensure the subject has a child dictionary to store predicates
        if subject_name not in graph_dict:
            graph_dict[subject_name] = {}

        # Ensure the predicate has a child list to store objects
        # We store the objects (values) as lists because sometime there is more than 1 value
        # E.g. child lithologies
        if predicate_name not in graph_dict[subject_name]:
            graph_dict[subject_name][predicate_name] = []

        # Add the new object to the dictionary
        graph_dict[subject_name][predicate_name].append(object_)

print(f"Found {len(graph_dict)} lithologies in triplestore!")
```

```
Found 265 lithologies in triplestore!
```

We now have a dictionary representation of our triplestore lithology classifications!
We can use this to find the data for `Rhyolite`, which was mentioned in our earlier example.

```python
# Import pretty printer to output the dictionary nicely
from pprint import pprint
pprint(graph_dict["rhyolite"])
```

```
{'altLabel': [rdflib.term.Literal('Liparit', lang='de'),
              rdflib.term.Literal('liparit', lang='ru'),
              rdflib.term.Literal('lipariitti', lang='fi'),
              rdflib.term.Literal('ryolit', lang='sv'),
              rdflib.term.Literal('liparita', lang='es'),
              rdflib.term.Literal('liparite', lang='it')],
 'broader': [rdflib.term.URIRef('http://resource.geosciml.org/classifier/cgi/lithology/rhyolitoid')],
 'definition': [rdflib.term.Literal('rhyolitoid in which the ratio of plagioclase to total feldspar is between 0.1 and 0.65.', lang='en')],
 'exactMatch': [rdflib.term.URIRef('http://inspire.ec.europa.eu/codelist/LithologyValue/rhyolite')],
 'example': [rdflib.term.Literal('liparite', lang='en'),
             rdflib.term.Literal('rhyodacite', lang='en')],
 'inScheme': [rdflib.term.URIRef('http://resource.geosciml.org/classifierscheme/cgi/2016.01/simplelithology')],
 'prefLabel': [rdflib.term.Literal('ryolit', lang='sv'),
               rdflib.term.Literal('流紋岩', lang='ja'),
               rdflib.term.Literal('หินไรโอไรต์', lang='th'),
               rdflib.term.Literal('riolite', lang='it'),
               rdflib.term.Literal('rhyolite', lang='en'),
               rdflib.term.Literal('流纹岩', lang='zh'),
               rdflib.term.Literal('ryolit', lang='vi'),
               rdflib.term.Literal('Rhyolith', lang='de'),
               rdflib.term.Literal('유문암', lang='ko'),
               rdflib.term.Literal('riolit', lang='id'),
               rdflib.term.Literal('¹ó\xadÄëÂºÄìª', lang='lo'),
               rdflib.term.Literal('riolita', lang='es'),
               rdflib.term.Literal('ryoliitit', lang='fi'),
               rdflib.term.Literal('riolit', lang='ms'),
               rdflib.term.Literal('riolit', lang='ru'),
               rdflib.term.Literal('rhyolite', lang='fr'),
               rdflib.term.Literal('silarIyU:lIt', lang='km')]}
```

If we want to see its parents, we can access the object (value) behind the predicate (attribute) `broader`.

```python
broader_uris = graph_dict["rhyolite"]["broader"]
parents = [
    uri.removeprefix(lithology_prefix)
    for uri in broader_uris
]
pprint(parents)
```

```
['rhyolitoid']
```

Finally, in this format of linked data, recursive functions are incredibly useful to traverse a graph
from one node to another. Or, in the case of `triples`, from one subject (row) to another. Here, we will
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
    if "broader" in graph_dict[target_lithology]:

        # Get the current parents
        current_parents = {
            uri.removeprefix(lithology_prefix)
            for uri in graph_dict[target_lithology]["broader"]
        }

        # Add the current parents to the list of all parents
        parents = parents.union(current_parents)

        for parent_lithology in current_parents:
            # Find the parents of the parent
            parent_parents = find_lithology_parents(graph_dict, parent_lithology, parents)
            # Add the parents of the parent to the set of all parents
            parents = parents.union(parent_parents)

    return parents


rhyolite_parents = find_lithology_parents(graph_dict, "rhyolite")
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

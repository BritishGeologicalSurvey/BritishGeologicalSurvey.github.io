---
title:  "Exposing and resolving persistent identifiers on the web"
author: Rachel Heaven
categories:
  - Open Data
tags:
  - Linked Data
  - RDF
---

## What are persistent identifiers?

Within our internal corporate databases we have well managed persistent identifiers for most of our important data items, in the form of foreign key columns in relational databases. These are either auto-incrementing integers or a short text code.  They uniquely identify a record, can be used to reference it from other database tables and are not allowed to be changed. The codes are guaranteed to be unique within that set of data, but they may not be unique across BGS's other data resources and are certainly not unique outside BGS.

We want to make our data publicly available in the [Web of Data](https://www.w3.org/2013/data/) and as such each item should have a universally unique identifier on the web in the form of a persistent URI, which can similarly be used to uniquely identify a resource and reference it from anywhere in the web. You can read more about this in the [W3C Data on the Web Best Practices](https://www.w3.org/TR/dwbp/#DataIdentifiers) and the original concept from [Tim Berners Lee's 5 stars of Linked Data](https://www.w3.org/DesignIssues/LinkedData.html)

![Tim Berners-Lee, CC0, via Wikimedia Commons](https://upload.wikimedia.org/wikipedia/commons/3/30/Tim_Berners-Lee_5-star_Open_Data_plan.png)

## How are we converting our internal identifiers to URIs?

For each dataset we define a sub-domain under ``http://data.bgs.ac.uk/id`` , for example:

``http://data.bgs.ac.uk/id/dataHolding/``  for our data catalogue (metadata) entries

Sometimes the URL may contain another part in the path to group identifiers that belong to a larger concept scheme, for example: 

``http://data.bgs.ac.uk/id/Lexicon/NamedRockUnit/``  for our rock formations described in the [BGS Lexicon of Named Rock Units](https://www.bgs.ac.uk/technologies/the-bgs-lexicon-of-named-rock-units/)

We append the integer or text code from each item in the database to the appropriate URI subdomain stem, for example:
 
``http://data.bgs.ac.uk/id/dataHolding/13606914``

``http://data.bgs.ac.uk/id/Lexicon/NamedRockUnit/OXC``

This is where we had a problem: some of these datasets pre-date the World Wide Web and Linked Data, and a small proportion of the text identifiers contained characters that are illegal or problematic when included in a URL. The codes are widely used in internal database references and used in key datasets such as our digital geological mapping and borehole logging, so we couldn't update them at source without having to do a lot of unpicking. To solve this, we created and used a secondary unique key on these database tables where the illegal characters were substituted with a legal character (e.g. ``H`` instead of ``#``) using an easily reversible algorithm, making sure we maintained uniqueness.

## How are we exposing these on the web?


We run nightly scripts through a gitlab scheduled ci/cd pipeline, which query our relational database and generate linked data triples declaring each of these URIs as types of [skos:Concept](https://www.w3.org/2009/08/skos-reference/skos.html#Concept)

(The scripts actually construct lots of other triples to serialise other information that we know about those concepts too - that's another story.)

For some datasets we have a separate application that provides the landing page and search functionality for that dataset (for example we use Geonetwork for our data catalogue). In these cases we also construct a triple that associates the concept with the URL of its landing page using the [foaf:homepage](http://xmlns.com/foaf/spec/#term_homepage) predicate.

As part of the scheduled pipeline, all the triples are updated nightly to https://github.com/BritishGeologicalSurvey/vocabularies
and the triples are re-loaded into our Apache Jena Fuseki triplestore.  

The linked data is exposed to the web using nginx and a Linked Data API written using the Python based Falcon web framework. 

## How do we redirect to a user friendly web page or application?


The API handles content negotiation for different resource description framework (RDF) formats and uses [rdflib](https://github.com/RDFLib/rdflib) for serialisation.  The representation type requested by the client can be indicated by file type extension in the URL, with text/html as the default: 

 - `.html` or no extension will return text/html

 - `.nt` will return n-triples

 - and so on for other machine readable formats: .rdf, .ttl, .json , .xml
 
If the content type of text/html is requested then the API checks for existence of a `foaf:homepage` predicate in the graph, and redirects to the URL in the object of that triple if one is found. If a ``foaf:homepage`` predicate is not found then the API uses Jinja2 HTML templates to display all known triples for that concept within the http://data.bgs.ac.uk site.


    def redirect_in_graph(graph):
         """Check for the presence of a redirect triple in a graph"""
         for subj, pred, obj in graph.triples((None, FOAF.homepage, None)):
             return str(obj)
         return None

You can see this redirect in action with the data catalogue entries:

http://data.bgs.ac.uk/id/dataHolding/13606914.nt (note `.nt` extension) doesn't trigger the redirect and returns the minimal set of triples serialised in n-triples format for machine processing 

    <http://data.bgs.ac.uk/id/dataHolding/13606914> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://rdfs.org/ns/void#Dataset> .
    <http://data.bgs.ac.uk/id/dataHolding/13606914> <http://www.w3.org/2004/02/skos/core#inScheme> <http://data.bgs.ac.uk/ref/DiscoveryMetadata> .
    <http://data.bgs.ac.uk/id/dataHolding/13606914> <http://xmlns.com/foaf/0.1/homepage> <http://metadata.bgs.ac.uk/geonetwork/srv/eng/catalog.search#/metadata/33bec698-1d9a-6dee-e054-002128a47908> .


http://data.bgs.ac.uk/id/dataHolding/13606914 or http://data.bgs.ac.uk/id/dataHolding/13606914.html (using no extension or `.html`) redirect to the appropriate Geonetwork page under http://metadata.bgs.ac.uk/geonetwork that you see in the foaf triple above

![Geonetwork landing page for dataset id 13606914](../../assets/images/2021-08-11-persistent-identifiers/geonetwork.png)


## Why is this good?

If we change the application that handles our data we don't need to change the URIs for the data, we just change the `foaf:homepage` value in the triples. This means the URIs are safely persistent and we can swap and change the application and server that we use to publish the data. We can share the URIs as widely as we want, they can be used in other people's datasets to create linkages, and they will always mean the same thing and should always be able to queried on the web to describe what that thing is.

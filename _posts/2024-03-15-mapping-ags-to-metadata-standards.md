---
title: 'Can we get metadata from AGS data?'
author: Edd Lewis
categories:
  - Development
tags:
  - ags
  - boreholes
  - metadata
  - "19115"
  - gemini
  - medin

---
# Can we get metadata from AGS data? ISO 19115 - DCAT - Schema.org – AGS ile Format mapping

## Introduction

Although the AGS file format is not a metadata standard it does contain elements which could potentially be mapped to existing metadata standards, facilitating creation of formal metadata from AGS data.

This document a mapping exercise between <u>[ISO 19115](https://en.wikipedia.org/wiki/Geospatial_metadata):2003</u>, [<u>DCAT</u>](https://www.w3.org/TR/vocab-dcat/),<u>[Schema.org](http://schema.org/) (v 3.3)</u> and the AGS file format and is based on the W3C work - <https://www.w3.org/2015/spatial/wiki/ISO_19115_-_DCAT_-_Schema.org_mapping>.

The mappings here defined are based on the following reference documentation:

- [<u>ISO 19115 to Schema.org mapping defined in the Geonovum
  > testbed</u>](http://geo4web-testbed.github.io/topic4/#h.slcmhsi0iksl) ([<u>XSLT
  > implementation</u>](https://github.com/geo4web-testbed/core-geonetwork/blob/schema_org/schemas/iso19139/src/main/plugin/iso19139/formatter/schema-org/view.xsl))

- [<u>GeoDCAT-AP</u>](https://joinup.ec.europa.eu/node/139283)

- [<u>DCAT-AP to Schema.org
  > mapping</u>](https://ec-jrc.github.io/dcat-ap-to-schema-org/)

- Ahmad Assaf, Raphaël Troncy, Aline Senart (2015). [<u>HDL - Towards a
  > Harmonized Dataset Model for Open Data
  > Portals</u>](http://ceur-ws.org/Vol-1362/PROFILES2015_paper3.pdf). [<u>USEWOD-PROFILES
  > 2015</u>](http://ceur-ws.org/Vol-1362/), pages 62-74.

- [<u>DCAT to Schema.org mapping defined by Project Open
  > Data</u>](https://project-open-data.cio.gov/metadata-resources/)

- AGS Data Format v4.1.1 -
  > <https://www.ags.org.uk/content/uploads/2022/02/AGS4-v-4.1.1-2022.pdf>

## Attributes / properties

This section groups the mappings concerning attributes / properties based on the reference entities / classes.

Catalog

| **ISO 19115**                                 | **DCAT**                                                                                   | **Schema.org**                                                 | **Comments**                                                                                   | **AGS**   |
|-----------------------------------------------|--------------------------------------------------------------------------------------------|----------------------------------------------------------------|------------------------------------------------------------------------------------------------|-----------|
|                                               | [<u>catalog record</u>](https://www.w3.org/TR/vocab-dcat/#Property:catalog_catalog_record) | ??                                                             | A possible option is to use [<u>schema:itemListElement</u>](http://schema.org/itemListElement) |           |
|                                               | [<u>dataset</u>](https://www.w3.org/TR/vocab-dcat/#Property:catalog_dataset)               | [<u>schema:dataset</u>](http://schema.org/dataset)             |                                                                                                |           |
| Resource abstract                             | [<u>description</u>](https://www.w3.org/TR/vocab-dcat/#Property:catalog_description)       | [<u>schema:description</u>](http://schema.org/description)     |                                                                                                | TRAN_DESC |
| Online resource (function: "information")     | [<u>homepage</u>](https://www.w3.org/TR/vocab-dcat/#Property:catalog_homepage)             | [<u>schema:url</u>](http://schema.org/url)                     |                                                                                                |           |
| Resource language                             | [<u>language</u>](https://www.w3.org/TR/vocab-dcat/#Property:catalog_language)             | [<u>schema:inLanguage</u>](http://schema.org/inLanguage)       |                                                                                                |           |
| Resource contraints: use constraints          | [<u>license</u>](https://www.w3.org/TR/vocab-dcat/#Property:catalog_license)               | [<u>schema:license</u>](http://schema.org/license)             |                                                                                                |           |
| Responsible party (role: "publisher")         | [<u>publisher</u>](https://www.w3.org/TR/vocab-dcat/#Property:catalog_publisher)           | [<u>schema:publisher</u>](http://schema.org/publisher)         |                                                                                                | TRAN_PROD |
| Temporal reference: date of publication       | [<u>release date</u>](https://www.w3.org/TR/vocab-dcat/#Property:catalog_release_date)     | [<u>schema:datePublished</u>](http://schema.org/datePublished) |                                                                                                | TRAN_DATE |
| Resource constraints                          | [<u>rights</u>](https://www.w3.org/TR/vocab-dcat/#Property:catalog_rights)                 | ??                                                             |                                                                                                |           |
| Geographic extent                             | [<u>spatial</u>](https://www.w3.org/TR/vocab-dcat/#Property:catalog_spatial)               | [<u>schema:spatial</u>](http://schema.org/spatial)             |                                                                                                | PROJ_LOC  |
|                                               | [<u>themes</u>](https://www.w3.org/TR/vocab-dcat/#Property:catalog_themes)                 | ??                                                             |                                                                                                |           |
| Resource title                                | [<u>title</u>](https://www.w3.org/TR/vocab-dcat/#Property:catalog_title)                   | [<u>schema:name</u>](http://schema.org/name)                   |                                                                                                | PROJ_NAME |
| Temporal reference: date of last modification | [<u>update date</u>](https://www.w3.org/TR/vocab-dcat/#Property:catalog_update_date)       | [<u>schema:dateModified</u>](http://schema.org/dateModified)   |                                                                                                |           |

Metadata (ISO 19115) - Catalog record (DCAT)

| **ISO 19115**                            | **DCAT**                                                                                | **Schema.org**                                                 | **Comments**                                                             | **AGS**   |
|------------------------------------------|-----------------------------------------------------------------------------------------|----------------------------------------------------------------|--------------------------------------------------------------------------|-----------|
|                                          | [<u>description</u>](https://www.w3.org/TR/vocab-dcat/#Property:record_description)     | [<u>schema:description</u>](http://schema.org/description)     |                                                                          |           |
| Metadata date: date of publication       | [<u>listing date</u>](https://www.w3.org/TR/vocab-dcat/#Property:record_release_date)   | [<u>schema:datePublished</u>](http://schema.org/datePublished) |                                                                          | TRAN_DATE |
|                                          | [<u>primary topic</u>](https://www.w3.org/TR/vocab-dcat/#Property:record_primary_topic) | ??                                                             | A possible option is to use [<u>schema:item</u>](http://schema.org/item) |           |
|                                          | [<u>title</u>](https://www.w3.org/TR/vocab-dcat/#Property:record_title)                 | [<u>schema:name</u>](http://schema.org/name)                   |                                                                          | PROJ_NAME |
| Metadata date: date of last modification | [<u>update date</u>](https://www.w3.org/TR/vocab-dcat/#Property:record_update_date)     | [<u>schema:dateModified</u>](http://schema.org/dateModified)   |                                                                          | TRAN_DATE |

Dataset

| **ISO 19115**                                      | **DCAT**                                                                                | **Schema.org**                                                             | **Comments** | **AGS**                 |
|----------------------------------------------------|-----------------------------------------------------------------------------------------|----------------------------------------------------------------------------|--------------|-------------------------|
| Responsible party (role: "point of contact")       | [<u>contact point</u>](https://www.w3.org/TR/vocab-dcat/#Property:dataset_contactPoint) | [<u>schema:contactPoint</u>](http://schema.org/contactPoint)               |              | TRAN_PROD               |
| Resource description                               | [<u>description</u>](https://www.w3.org/TR/vocab-dcat/#Property:dataset_description)    | [<u>schema:description</u>](http://schema.org/description)                 |              | PROJ_MEMO or TRAN_DESC? |
| Distribution information                           | [<u>distribution</u>](https://www.w3.org/TR/vocab-dcat/#Property:dataset_distribution)  | [<u>schema:distribution</u>](http://schema.org/distribution)               |              |                         |
| Maintenance information: maintenance frequency     | [<u>frequency</u>](https://www.w3.org/TR/vocab-dcat/#Property:dataset_frequency)        | ??                                                                         |              | TRAN_STAT               |
| Resource identifier                                | [<u>identifier</u>](https://www.w3.org/TR/vocab-dcat/#Property:dataset_identifier)      | [<u>schema:identifier</u>](http://schema.org/identifier)                   |              | PROJ_ID                 |
| Descriptive keyword (free text)                    | [<u>keyword</u>](https://www.w3.org/TR/vocab-dcat/#Property:dataset_keyword)            | [<u>schema:keywords</u>](http://schema.org/keywords)                       |              |                         |
| Online resource (function: "information")          | [<u>landing page</u>](https://www.w3.org/TR/vocab-dcat/#Property:dataset_landingpage)   | [<u>schema:url</u>](http://schema.org/url)                                 |              | FILE_FSET               |
| Resource language                                  | [<u>language</u>](https://www.w3.org/TR/vocab-dcat/#Property:dataset_language)          | [<u>schema:inLanguage</u>](http://schema.org/inLanguage)                   |              |                         |
| Responsible party (role: "publisher")              | [<u>publisher</u>](https://www.w3.org/TR/vocab-dcat/#Property:dataset_publisher)        | [<u>schema:publisher</u>](http://schema.org/publisher)                     | .            | TRAN_PROD               |
| Temporal reference: date of publication            | [<u>release date</u>](https://www.w3.org/TR/vocab-dcat/#Property:dataset_release_date)  | [<u>schema:datePublished</u>](http://schema.org/datePublished)             |              | TRAN_DATE               |
| Geographic extent                                  | [<u>spatial coverage</u>](https://www.w3.org/TR/vocab-dcat/#Property:dataset_spatial)   | [<u>schema:spatialCoverage</u>](http://schema.org/spatialCoverage)         |              | PROJ_LOC                |
| Temporal extent                                    | [<u>temporal coverage</u>](https://www.w3.org/TR/vocab-dcat/#Property:dataset_temporal) | [<u>schema:datasetTimeInterval</u>](http://schema.org/datasetTimeInterval) |              |                         |
| Descriptive keyword (from a controlled vocabulary) | [<u>theme</u>](https://www.w3.org/TR/vocab-dcat/#Property:dataset_theme)                | [<u>schema:about</u>](http://schema.org/about)                             |              | LOCA_STAR & LOCA_ENDD   |
| Resource title                                     | [<u>title</u>](https://www.w3.org/TR/vocab-dcat/#Property:dataset_title)                | [<u>schema:name</u>](http://schema.org/name)                               |              | PROJ_NAME               |
| Temporal reference: date of last modification      | [<u>update date</u>](https://www.w3.org/TR/vocab-dcat/#Property:dataset_update_date)    | [<u>schema:dateModified</u>](http://schema.org/dateModified)               |              |                         |

## Distribution

The mapping of "distributions" poses some issues, because of a mismatch between the conceptual models in ISO 19115, DCAT and AGS.

- DCAT:

  - A dataset can be associated with 0 or more distributions.

  - Format and use / access conditions are properties of distributions,
    > and not of datasets.

- ISO 19115:

  - A resource can have at most 1 distribution, which may be associated
    > with 0 or more online resources. The format is specified at the
    > level of the distribution, whereas the access URL is specified in
    > the associated online resources.

  - Use and access conditions are specified at the level of the dataset.

- AGS:

  - An AGS file can specify an associated file of supplementary data,
    however in the context of a distribution the metadata standards are
    referring to the source data AGS file itself not accessory files.

A possible solution to deal with this issue needs to be devised and agreed upon. Meanwhile, in its current version, the following table does not include mappings concerning ISO 19115 elements on distribution format and dataset use / access constraints.

| **ISO 19115**                                                     | **DCAT**                                                                                    | **Schema.org**                                                   | **Comments**                 | **AGS**   |
|-------------------------------------------------------------------|---------------------------------------------------------------------------------------------|------------------------------------------------------------------|------------------------------|-----------|
| Online resource (function: "download"): linkage                   | [<u>access URL</u>](https://www.w3.org/TR/vocab-dcat/#Property:distribution_accessurl)      | [<u>schema:contentURL</u>](http://schema.org/contentURL)         | FILE_FSET not usually online | FILE_FSET |
|                                                                   | [<u>byte size</u>](https://www.w3.org/TR/vocab-dcat/#Property:distribution_size)            | [<u>schema:contentSize</u>](http://schema.org/contentSize)       |                              |           |
| Online resource (function: "download"): description               | [<u>description</u>](https://www.w3.org/TR/vocab-dcat/#Property:distribution_description)   | [<u>schema:description</u>](http://schema.org/description)       |                              | FILE_DESC |
| Online resource (function: "download"): linkage                   | [<u>download URL</u>](https://www.w3.org/TR/vocab-dcat/#Property:distribution_downloadurl)  | [<u>schema:contentURL</u>](http://schema.org/contentURL)         |                              |           |
|                                                                   | [<u>format</u>](https://www.w3.org/TR/vocab-dcat/#Property:distribution_format)             | [<u>schema:encodingFormat</u>](http://schema.org/encodingFormat) |                              | FILE_TYPE |
|                                                                   | [<u>license</u>](https://www.w3.org/TR/vocab-dcat/#Property:distribution_license)           | [<u>schema:license</u>](http://schema.org/license)               |                              |           |
|                                                                   | [<u>media type</u>](https://www.w3.org/TR/vocab-dcat/#Property:distribution_media_type)     | [<u>schema:fileFormat</u>](http://schema.org/fileFormat)         |                              | FILE_TYPE |
| Online resource (function: "download"): date of publication       | [<u>release date</u>](https://www.w3.org/TR/vocab-dcat/#Property:distribution_release_date) | [<u>schema:datePublished</u>](http://schema.org/datePublished)   |                              | FILE_DATE |
|                                                                   | [<u>rights</u>](https://www.w3.org/TR/vocab-dcat/#Property:distribution_rights)             | ??                                                               |                              |           |
| Online resource (function: "download"): title                     | [<u>title</u>](https://www.w3.org/TR/vocab-dcat/#Property:distribution_title)               | [<u>schema:name</u>](http://schema.org/name)                     |                              | FILE_NAME |
| Online resource (function: "download"): date of last modification | [<u>update date</u>](https://www.w3.org/TR/vocab-dcat/#Property:distribution_update_date)   | [<u>schema:dateModified</u>](http://schema.org/dateModified)     |                              |           |

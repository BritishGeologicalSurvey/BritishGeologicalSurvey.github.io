---
title:  "Importing Balsamiq wireframes into Figma, an experiment with the Figma plugin API"
author: Andy Bean
categories:
  - UI-UX
  - Design Tools
tags:
  - Figma
  - Balsamiq
  - Design Tools
---

## Introduction
The [Micronutrient Action Policy Support (MAPS)](https://micronutrient.support) project aims to produce a web-hosted decision support tool to allow users to estimate micronutrient deficiencies in Sub-Saharan African nations and explore pathways to improve nutrition.  BGS Digital are leading the design and software development aspects of this multi-institute project.

This post describes a proof of concept Figma plugin which was developed to aid the developer workflow when developing and testing wireframes and application mockups.

## Building Wireframes

In the early stages of the system design, we have made extensive use of [Balsamiq](https://balsamiq.com/wireframes/) as a tool for producing low-fidelity wireframes to mock-up the user flow and navigation through the tool.  These wireframes are quick to produce and easy to test and iterate on user journeys without getting caught up on details of colour schemes, fonts, imagery etc.  Later design stages have used [Figma](https://www.figma.com/) to produce higher fidelity mock-ups ready for implementation by the front-end development team.

![Low and higher fidelity wireframes using Balsamiq (left) and Figma (right)](../../../assets/images/2021-08-11-balsamiq_to_figma/wireframes.png)

*Low and higher fidelity wireframes using Balsamiq (left) and Figma (right)* [Source: MAPS Project]

## Remote Testing - Great for Figma, trickier for Balsamiq

In the early stages of the project, the majority of the [co-design](https://micronutrient.support/co-design/) and user testing was planned and conducted in person.  However the lockdowns and cessation of travel in 2020 meant remote methods had to be employed.  Alongside tools such as [Zoom](https://zoom.us/) and [Miro](https://miro.com/login/), we were fortunate to be able to utilise the dedicated user testing tools [Usability Hub](https://usabilityhub.com/) and [Useberry](https://www.useberry.com/) to test how users might flow and navigate through the system

![Insights into user flows through the application from Useberry](../../../assets/images/2021-08-11-balsamiq_to_figma/useberry.png)

*Insights into user flows through the application from [Useberry](https://www.useberry.com/) testing* [Source: MAPS Project]

Tools such as Useberry allow direct importing of Figma prototypes into online tests via the Figma API but there are not equivalent workflows for wireframes built using Balsamiq.

We were reluctant to give up on Balsamiq due to both the existing time investment in building wireframes and the buy-in and acceptance of this approach from stakeholders and the wider project team.

Useberry allows you to create wireframe flows by uploading and linking individual images via the web UI but this is impractical for wireframes of any decent size or where frequent changes and iterations are expected.  Another solution was required and so we turned to the Figma Plugin API in an attempt to import Balsamiq mockups into Figma.

## The balsamiq2figma Plugin

Figma allows the community to create [plugins](https://www.figma.com/community) using web technologies to enhance and add new functionality to the app.  There are various sandboxing and security hurdles which are beyond the scope of this post but can be found in their [documentation](https://www.figma.com/plugin-docs/how-plugins-run/).

Balsamiq desktop stores wireframes in *.bmpr* files.  These are in fact just a [SQLite database](https://balsamiq.com/wireframes/cloud/docs/bmpr-format/) which contains (amongst other things) the various pages of the wireframe and the co-ordinates and sizes of the controls on each wireframe page.  Luckily we can open and query this database in web technologies using [sql.js](https://github.com/sql-js/sql.js/).

Recreating the UI elements used in Balsamiq and their distinctive 'sketchy' style within Figma would be a huge undertaking. However Balsamiq has the functionality to export static png images of each page of the wireframe.  If these images are imported as 'frames' within Figma, new click areas to link frames can programatically be created within Figma using the size and co-ordinates data from the Balsamiq database.  The result will be a visually identical output maintaining the simple click-based interactivity from the original mockup.

### Bringing it all together

The balsamiq2figma plugin performs the following steps:

1. User selects the .bmpr Balsamiq file and a zip file of .png screen outputs from Balsamiq
2. The plugin generates a figma frame for each mockup page, using the png screen output as its background
3. The plugin creates rectangles overlaid on the mockup frame in the positions and sizes of the interactive Balsamiq elements using data from the .bmpr SQLite database.  These are filled in a semi-transparent pinkish fill to match the default Balsamiq output.

![The Balsamiq2Figma plugin interface](../../../assets/images/2021-08-11-balsamiq_to_figma/balsamiq2figma.png)

*The Balsamiq2Figma plugin interface* 

### So close, but yet so far!

Unfortunately the Figma plugin (currently) does not support programatically creating links between nodes for navigation in 'prototype' mode.  The API does however allow read-only access to the existing links of a given node.

Whilst this means that the linking of frames cannot be completely automated, the ability to check for the existence of a connection allowed for a 'wizard' mode to be created to make the manual creation of the links as quick and simple as possble.

![The balsamiq2figma wiring wizard](../../../assets/images/2021-08-11-balsamiq_to_figma/wiring.gif)

*The balsamiq2figma wiring wizard* 

## Summary

In order to be able to continue to use Balsamiq wireframes within modern online testing platforms, we developed a plugin for Figma to allow a static image representation of the pages of a Balsamiq wireframe to be automatically imported into Figma with the interactive links then re-created using native Figma elements.

Limitations to the Figma plugin API stopped this from being a fully automated process, though hopefully this will become a viable option in the future.

The initial development of this plugin was as closed-source proof of concept, though we are considering releasing it as an open source package in the future.

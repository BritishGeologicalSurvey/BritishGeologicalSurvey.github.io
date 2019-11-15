---
title:  "Tools for creating sharing and managing design systems (Part 2)"
author: Paulius Tvaranavicius
categories:
  - UI-UX
tags:
  - design system
  - css
  - scss
  - sass
---

This is **part 2** in a blog series about our approach to creating a shared design system for [myHAZ-VCT PLATFORM](https://oda.bgs.ac.uk/).

- [Part 1 - What are design systems?](../myhaz-design-system-1)
- Part 2 - Tools for creating sharing and managing design systems
- [Part 3 - One of many ways to create a design system](../myhaz-design-system-3)
- [Part 4 - Does every project need a design system?](../myhaz-design-system-4)

## How do you know if you need a design system?

[myHAZ-VCT PLATFORM](https://oda.bgs.ac.uk/) seemed like a good candidate to benefit from a design system. It's a service/platform made of three different but related applications. All of them share a purpose of disseminating hazard observations. 

Here are a few of the reasons why we decided to jump on the band wagon of design systems as well: 

- consistent look - we wanted the three different applications to feel like part of the same product
- improved user experience - people switching between different platforms would learn the new interactions quicker
- efficiency - remove duplicate effort (even though the three applications are different, they share many elements)
- customization - to be able to adapt the application in new contexts in the future (create new themes more easily)

## Tools for creating and maintaining design systems

There are many tools to help you with design system creation. They range from design centric to code centric and everything in between. 

Here are some examples of these tools:
- [Storybook](https://storybook.js.org/)
- [InVision Design System Manager](https://www.invisionapp.com/design-system-manager)
- [Pattern Lab](https://patternlab.io/)
- [UXPin](https://www.uxpin.com/)
- [Fractal](https://fractal.build/)
- [KSS](https://warpspire.com/kss/)
- [Sketch](https://www.sketch.com/)
- [Figma](https://www.figma.com/), etc.

Our main requirements for the design system tool was for it be easily accessible by all developers, quick to update and easy to document. So we settled on the [KSS node](https://github.com/kss-node/kss-node). It's a node.js implementation of [KSS](https://warpspire.com/kss/): a methodology for documenting and sharing stylesheets.

![An example of a documented KSS component](../../assets/images/2019-11-01-myhaz-design-system/documenting-kss.png)
*An example of a documented component*

Basically, it's a static site generator that converts scss files and corresponding documentation into a website where those components and their code can be previewed.

![Comments and related scss code are compiled into a static website](../../assets/images/2019-11-01-myhaz-design-system/static-website-for-design-system.png)
*Comments and related scss code are compiled into a static website*

You can find a useful guide on [csstricks.com](https://css-tricks.com/build-style-guide-straight-sass/) on how to set it up.

**[Part 3 - One of many ways to create a design system](../myhaz-design-system-3)**

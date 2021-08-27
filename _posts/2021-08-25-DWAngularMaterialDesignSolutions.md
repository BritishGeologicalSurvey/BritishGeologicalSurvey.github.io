---
title: "Utilising the Angular Material Library to Provide Bespoke Design Solutions"
author: Daniel Warren
categories:
  - front-end-development
  - ux-design
tags:
  - Angular
  - UX
  - GUI
---


The [Angular Material Library](https://material.angular.io/) is a collection of Material Design components which integrates with [Angular](https://angular.io/), a typescript based, open-source web development framework. The UI elements that the library provides are:

- Versatile: the same elements can be used on a desktop or mobile browser.
- Modifiable: elements can be adapted to suit unique design requirements.
- Styleable: styles can be created and applied to all elements in a project, allowing for colour schemes to be lifted from a UX/UI Designer's prototype and applied during development.

For these reasons Angular has become the foremost development framework within BGS Digital for application development, web development, and PWA (progressive web app) development.

![Demo-Mobile](https://github.com/DanielLyleWilliamWarren/BlogDay_AngularMaterial/raw/main/assets/opacitysolution.gif)

_Figure 1: Side navigation bar with bespoke solution to adjusting layer opacity in a mobile layout, the BGS colour scheme has been applied to all elements._

The above graphic shows a design solution implemented to address the requirement for a 'Layer Options Panel'. This was achieved by using a collection of elements from the Material Library, some straight out of the box such as the side navigation panel which has been populated with BGS Explorer specific content, and the dropdown menus which host the 'Layer Options Panel'. Some material elements have been modified to fit the requirements of the design such as the 'Opacity Slider' which is a dropdown menu with certain functionalities hidden from the user. All elements however have the same 'BGS Explorer' specific styling applied.

| BGS Explorer    | BMGF-MAPS |
| ----------- | ----------- |
| ![Demo-Notification](https://github.com/DanielLyleWilliamWarren/BlogDay_AngularMaterial/raw/main/assets/2MTJrwqEC0.gif) | ![Demo-Notification](https://github.com/DanielLyleWilliamWarren/BlogDay_AngularMaterial/raw/main/assets/MNTsDmZwKi.gif) |

_Figure 2: Example of the same UI notification component being used in different projects, where styling respective to each project is applied._

The Angular Material Library has allowed developers to work on multiple projects while utilising the same reusable UI components across multiple codebases. In the graphics shown above we see two different BGS projects - BGS Explorer and BMGF-MAPS, both using the same reusable notification component in the code, but with their own respective styling. The versatility of the Angular Material component is also demonstrated as it adapts to being displayed on a browser window and a mobile window.

To sum up, Angular is a very flexible framework offering in-house solutions to many developer headaches from routing to PWA support. With the Angular Material Library enhancing the toolkit at a developers disposal, developers and designers are in a better position to design user friendly GUIs and provide unique design solutions.

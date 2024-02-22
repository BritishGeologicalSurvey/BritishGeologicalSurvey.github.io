---
title: 'Refactoring web GIS map components'
author: Janusz Lavrnja-Czapski
categories:
  - Development
tags:
  - javascript
  - typescript
  - best practices
  - web gis
---

### The problem:

In the context of the VENTURA VDR, we have recently received the go-ahead to create an open-source version of the project, which will be hosted on GitHub and open to future collaboration from the wider scientific/development community. This has prompted us to consider how we can get the codebase into a state where it is well-documented, organized, and ready for contributions.

Across other BGS projects where we work with Leaflet/ESRI web maps, we have found ourselves in a situation where the component that initializes the map ends up containing large amounts of functionality and quickly becomes bloated. Since the web map is generated via library code, the approach to building applications centered around the map differs architecturally from a standard component-based application, as we can’t utilize HTML templates for display logic. This leads to the creation of elements and interaction with them being implemented with TypeScript/JavaScript methods.

The aim of this refactor is to untangle all the operations in our map.component.ts file.

### The approach:

- Identify common functionalities.

- Extract each of these functionalities into dedicated services.

- Create a singleton service for passing data between components and services.

- Identify areas where complexity can be reduced or better managed.

Within the VENTURA VDR, the main operations being performed are: creating labels, generating HTML pop-ups, interacting with the map, creating layers, and visualizing layers. Below is an indication of the structure we created to organize the functionality:

`label-data.service.ts`

`label-presentation.service.ts`

`data.service.ts`

`interaction.service.ts`

`layer.service.ts`

`map.service.ts`

`popup.service.ts`

`visualization.service.ts`

Once these services were created, we split the functionality from the existing map component into each of the dedicated files. One particularly noteworthy service is the data.service.ts file. It was created as a singleton service so that it could be used across the whole application and not restricted to one particular module.

Inside, it contains a series of getters and setters for data variables that need to be shared between services and components.

```typescript
public get map(): L.Map {
  return this.leafletMapObj;
}

public set map(map: L.Map) {
  this.leafletMapObj = map;
}

public get timePeriod(): ResultTimePeriod {
  return this.activeTimePeriod;
}

public set timePeriod(activeTimePeriod: ResultTimePeriod) {
  this.activeTimePeriod = activeTimePeriod;
}

public get scenario(): AllScenarios {
  return this.activeScenario;
}

public set scenario(activeScenario: AllScenarios) {
  this.activeScenario = activeScenario;
}
```

It can then be called in the following manner:

```typescript
this.dataService.scenario = scenarioData;

this.processSomeData(this.dataService.scenario);
```

Creating this structure allowed us to slim down our map.component.ts file from over 1000 lines to just over 250. Having a well-defined separation of concerns makes it easy for new developers to the project to clearly understand the operations being carried out and allows for simple integration of new functionality.

### Takeaways:

Moving forward, we believe there will be significant value in considering a services-based architecture for our Angular applications that implement a web GIS. This will enable us to build solutions that are well-organized from the start and can scale as the project complexity and lifespan increase.

Further reading can be found [here.](https://medium.com/@snehalv.2010/angular-service-architecture-9e907c96be04).


---
title:  "BGS contribution to Parse Server open-source platform"
author: andybean
categories:
  - open-source
tags:
  - Parse-Server
  - MBaaS
  - Docker
  - GitHub
  - continuous-integration
---

A number of BGS projects are using the open source [Parse Server](https://parseplatform.org/) platform.  Previously an MBaaS (mobile backend as a service) purchased by Facebook in 2013, Parse was closed in 2017 and subsequently open-sourced under the [Parse Community](https://github.com/parse-community) GitHub organisation.

Along with a number of internal systems and soon to be released applications, Parse Server is used by BGS, most notably, as the backend system for user authentication in the crowd-sourcing aspects of the [iGeology app](https://www.bgs.ac.uk/iGeology/) on iOS. 

![Crowd-sourcing in iGeology iOS](../../assets/images/2019-12-10-bgs-contribution-to-parse-server-open-source-platform/iGeologyAccounts.png)

*User accounts for crowd-sourcing in iGeology iOS*

This article explains a small open-source contribution made by BGS to part of the Parse Platform to improve the efficiency, memory usage and start-up time of the Parse Dashboard application.

## Parse Platform and Docker

The Parse platform is comprised of three components:

 - A [MongoDB](https://www.mongodb.com/) or [PostgreSQL](https://www.postgresql.org/) database
 - [Parse-Server](https://github.com/parse-community/parse-server): the core of the platform comprising API, user management, push notifications etc.
 - [Parse-Dashboard](https://github.com/parse-community/parse-dashboard): an administrative console for managing data

![Parse Dashboard administrative interface](../../assets/images/2019-12-10-bgs-contribution-to-parse-server-open-source-platform/parse-dashboard.png)

*Parse Dashboard administrative interface* [Source: Parse Platform]

All aspects of the platform can be run as [Docker containers](https://www.docker.com/resources/what-container) which is the preferred approach at BGS as we move towards a more microservice-focussed infrastructure.

## Parse Dashboard Dockerfile

Parse Dashboard is a relatively simple web application built using [React](https://reactjs.org/) and the Parse Server API to access data.  [Webpack](https://webpack.js.org/) is used for transpilation and bundling of files at build time.

The Dockerfile for Parse Dashboard did some of the webpack processing when the Docker image was built, but some webpack processing occurred at the point the container was launched.  

This means that the image was larger than necessary as it had to contain dependencies (e.g. webpack) which would not be needed for a simple static web-server.  There was also a time delay between launching the container and the web UI being accessible.

When operating in a Continuous Integration and Continuous Delivery (CI/CD) environment, these delays were causing issues.

## BGS Contribution to Parse Dashboard

The BGS contribution to the Parse Dashboard project made two key contributions to the Dockerfile:

 - Switch from Debian base image to Alpine Linux
 - Switch from a single build stage to a multi-stage build

The details of the changes can be seen in the [Github Pull Request](https://github.com/parse-community/parse-dashboard/pull/912)

### Alpine Linux
[Alpine Linux](https://alpinelinux.org/about/) is a distribution of Linux specifically designed to be small, simple and secure which makes it ideal for Docker containers.

### Multi-stage build

[Multi-stage builds](https://docs.docker.com/develop/develop-images/multistage-build/) allow generation of temporary interim containers as part of the build process with the final output container only containing the necessary files from those parent containers.  

This means that in Parse Dashboard, the webpack compilation phases can occur within a *build stage* container containing a full node.js development environment, generating static HTML, CSS and JS files which are copied to the final *production* container which just needs a simple web-server to serve the static files.

![Docker multi-stage build](../../assets/images/2019-12-10-bgs-contribution-to-parse-server-open-source-platform/multi-stage.jpg)

*Docker multi-stage build* [Source: [Hakan Özler](https://www.slideshare.net/ozlerhakan/ignite-session-the-journey-of-multi-stage-builds-moby-project-and-linuxkit)]

This reduces the filesize, complexity and routes for potential security vulnerabilities in the final production container.

## Impact of changes

The impact of these changes on the launch time and memory footprint of the generated image was significant.  The delay between starting the container and the UI being available was reduced by nearly 95% along with a sizeable reduction in container size.

| | Container Build Time | Container Launch Time | Container Size |
|-------|--------|---------|---------|
| Previous Version | 1m 47.608s | 0m 25.552s | 320MB |
| BGS PR | 2m 42.572s | 0m 1.328s | 74.6MB |

*Impacts on build time, load time and memory usage*

This does come at the expense of some additional time when building the Docker image, but this is far outweighed by the other improvements.

The changes received positive responses from Parse Platform maintainers and other users of the platform:

> Thanks for the Pull Request! This surely will make the dashboard image lighter!

> It considerably slims down the result image, and we’re very happy about it!

> the improvement is very noticeable. both small imprint and fast - great work

The changes were released in [Version 1.3.0](https://github.com/parse-community/parse-dashboard/releases/tag/1.3.0) of Parse Dashboard.

## Conclusion

Whilst this was only a small contribution, it made a valuable improvement to an open-source project actively used by BGS.  I'm sure that there will be more to come as the project and our usage of the platform develops.

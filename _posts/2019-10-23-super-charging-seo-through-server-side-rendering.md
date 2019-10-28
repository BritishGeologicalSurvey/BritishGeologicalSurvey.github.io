---
title:  "Super-charging search engine optimisation (SEO) for JavaScript through server side rendering (SSR)"
author: Rehan Kaleem
categories:
  - DevOps
tags:
  - SEO
  - server-side-rendering
  - SSR
  - Rendertron
  - Docker
  - Puppeteer
  - Middleware
---

Single page applications (SPAs), are a modern way to write full web based experiences for audiences. Dev ops, frontend and backend teams can all work in unison to deliver a common vision without compromising design or function. This is because JavaScript (JS) fills in many of the gaps common to desktop applications that are not supported by standard HTML and CSS alone.

### What's the meta?
The bells and whistles that JS libraries can provide are often not without compromise. Search engine optimisation is an area that can be particularly challenging. Since search engines exclusively look at HTML, content buried within a JS application is not visible. Ultimately, this affects users who can’t rely on search engines to find the information of interest. One solution to this problem is to parse our JS application server-side (Server side rendering or SSR) and deliver the resulting HTML to the client. Rendertron is a tool to do this very thing! The <a href="https://ukgeos.ac.uk">UK Geoenergy Observatories</a> website is the first website from <a href="https://www.bgs.ac.uk/">BGS</a> to use SSR as a means for making data more discoverable through this method.

### The game has changed
Rendertron, developed by Google, works by running a headless instance of chrome on the server. After a request is made for a webpage, we use NGINX to identify each client through their client ID. Any search bot or crawler traffic is then diverted to our rendertron server. The rendertron server will parse our JS application and return information as static HTML, complete with its content.

![Rendertron process](https://developers.google.com/search/docs/guides/images/how-dynamic-rendering-works.png)
[Source: Dynamic Rendering with Rendertron](https://webmasters.googleblog.com/2019/01/dynamic-rendering-with-rendertron.html)

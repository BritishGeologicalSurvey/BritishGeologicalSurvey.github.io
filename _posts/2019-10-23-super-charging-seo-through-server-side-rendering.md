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

Our NGINX config file looks like this:

```bash
# Site-specific configuration for UKGEOS

# Configuration for IP addresses to skip logging f5 healthcheck pings
geo $log_ip {
    default 1;
}

upstream rendertron {
    server rendertron:3000;
}

# Server configuration
server {
    listen       80;
    server_name  localhost ukgeos.ac.uk *.ukgeos.ac.uk;
    access_log /var/log/nginx/access.log main if=$log_ip;
    charset utf-8;

    # Detect user agent of client
    set $prerender 0;
    # if user agent is a bot - set flag to 1
    if ($http_user_agent ~* "googlebot|yahoo|bingbot|baiduspider|yandex|yeti|yodaobot|gigabot|ia_archiver|facebookexternalhit|twitterbot|developers\.google\.com|slack|wget|WhatsApp") {
        set $prerender 1;
    }
    # otherwise set flag to 0
    if ($uri ~* "\.(js|css|xml|less|png|jpg|jpeg|gif|pdf|doc|txt|ico|rss|zip|mp3|rar|exe|wmv|doc|avi|ppt|mpg|mpeg|tif|wav|mov|psd|ai|xls|mp4|m4a|swf|dat|dmg|iso|flv|m4v|torrent|ttf|woff|svg|eot)") {
        set $prerender 0;
    }
    location / {
        root   /usr/share/nginx/html/;
        # send request to prerender service if user agent is detected
        if ($prerender = 1) {
            # SSR renderer server
            proxy_pass http://rendertron/render/https://ukgeos.ac.uk$request_uri;
        }


        # Angular is a single file app; there is no e.g. /data-details file, so
        # requests are redirected to /index.html for Angular to handle
        try_files $uri $uri/ /index.html;
    }
}
```

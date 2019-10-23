---
title:  "Super-charging SEO through server side rendering"
categories: 
  - DevOps
  - SEO
tags:
  - Server side rendering
  - SSR
  - Rendertron
  - Docker
  - puppeteer
  - middleware
---

Single page applications (SPAs), are a modern way to write full web based experiences for audiences. Dev ops, frontend and backend teams can all work in unison to deliver a common vision without compromising design or function. This is because JavaScript (JS) fills in many of the gaps common to desktop applications that are not supported by standard HTML and CSS alone.

## Whats the meta?
The bells and whistles that JS libraries can provide are often not without compromise. Search engine optimisation is an area that can be particularly challenging. Since search engines exclusively look at HTML, content buried within a JS application is not visible. Ultimately, this affects users who can’t rely on search engines to find the information of interest. One solution to this problem is to parse our JS application server-side and deliver the resulting HTML to the client. Rendertron is a tool to do this very thing!

## The game has changed
Rendertron, developed by Google, works by running a headless instance of chrome on the server. After a request is made for a webpage, we use NGINX to identify each client through thier client ID. Any search bot or crawler traffic is then diverted to our rendertron server. The rendertron server will parse our JS application and return information as static HTML, complete with it's content.

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

Setting up Rendertron was a straight forward process. We simply registered rendertron to our internal Docker registries:

```bash
FROM node:10-slim

# Install latest chrome dev package 
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
  && sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list' \
  && apt-get update \
  && apt-get install -y google-chrome-unstable fonts-ipafont-gothic fonts-wqy-zenhei fonts-thai-tlwg fonts-kacst ttf-freefont \
    --no-install-recommends \
  && rm -rf /var/lib/apt/lists/*

# Install puppeteer so it's available in the container.
RUN npm i puppeteer \
  # Add user so we don't need --no-sandbox.
  # same layer as npm install to keep re-chowned files from using up several hundred MBs more space
  && groupadd -r pptruser && useradd -r -g pptruser -G audio,video pptruser \
  && mkdir -p /home/pptruser/Downloads \
  && chown -R pptruser:pptruser /home/pptruser \
  && chown -R pptruser:pptruser /node_modules

WORKDIR /app

RUN curl -SL https://github.com/GoogleChrome/rendertron/archive/2ff347db7a643c36724cb3a274f2cb07bbb7a9f5.tar.gz | tar -vxz \
  && mv rendertron-2ff347db7a643c36724cb3a274f2cb07bbb7a9f5 rendertron

WORKDIR /app/rendertron

RUN npm install || \
  ((if [ -f npm-debug.log ]; then \
  cat npm-debug.log; \
  fi) && false) \
  && npm run build

# Run everything after as non-privileged user.
USER pptruser

EXPOSE 3000

ENTRYPOINT [ "npm" ]
CMD ["run", "start"]

```

The last step to get this working is to call up our registered rendertron server as a service for NGINX to point to: 

```bash
version: '3'
services:
  ukgeos-website:
    build:
      context: .
    ports:
      - ${PORT:-4200}:80
    environment:
            # external location
            - CONTENT_PATH=${CONTENT_PATH:-//SERVER:PORT/}
    restart: unless-stopped
    volumes:
      - ${PWD}/logs:/var/log/nginx
  
  rendertron:
    image: SERVER:PORT/path/to/rendertron:master
    ports:
      - ${PORT:-3000}:3000
    restart: unless-stopped

```

And that’s it! No tweaks to our actual website are needed, it’s all derived through configuration files.

With our NGINX and rendertron servers configured it becomes easy for us to bolt on our rendertron instance on to any project. An important step in making our data more discoverable to our users.


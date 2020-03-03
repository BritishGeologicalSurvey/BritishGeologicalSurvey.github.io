---
title:  "Technical Documentation & GitHub Pages"
author: Edd Lewis
classes: wide
categories:
  - Documentation
  - GitHub Pages
  - CL/CD
tags:
  - ReStructuredText
  - GitHub Pages
  - Pandoc
---

There are known challenges when publishing technical documentation / reports when using PDF or other desktop office formats which is why we endeavor at the BGS to publish our documentation using HTML

GOV.UK has a couple of good blog articles explaining the benefits of publishing to HTML over other formats. 

[GSD Blog Article 1](https://gds.blog.gov.uk/2018/07/16/why-gov-uk-content-should-be-published-in-html-and-not-pdf/)

[GDS Blog Article 2](https://phescreening.blog.gov.uk/2016/11/18/bye-bye-pdf-hello-html/)

The benefits are such that the Cabinet Office & Government Digital Services specify HTML5 in their [guidance for publishing government documents](https://www.gov.uk/government/publications/open-standards-for-government/viewing-government-documents) 

The BGS has been doing this for some time on a number of Projects/Services such as OneGeology & BGS Earthwise, however we hadn't yet done this for some legency documentation such as the user guide for our [BGS GroundHog software](https://www.bgs.ac.uk/research/environmentalModelling/groundhog/groundhogDesktop.html).

With the new release of GroundHog v2.0 we thought it would be a good time to look at migrating the documentation from MS Office/PDF to HTML. 

The solution we came to was based on the workflow of other technical documentation we write at the BGS, namely to use [Sphinx](www.sphinx-doc.org) to generate reStructuredText into HTML. 

However we also wanted to be more open in the work that we do, so chose to host the code of GitHub with the documentation website built sing Sphinx via Gitub Actions CI/CD and hosted on GitHub pages 

## Document Conversion  

The GroundHog documentation had already been written MS Word as a .docx 

![Worddoc](../assets/images/2020-02-03-Technical-Documentation/groundhog_word.PNG)

This had to be converted to HTML and the images extracted. 

To do this we used [pandoc](https://pandoc.org/), a universal document converter. 

pandoc was installed as explained in it's own documentation.

We than ran the following commands to 1. Convert the text and 2. extract the media/images.  

```bash
pandoc --extract-media=media -s -t rst BGS_Groundhog_Desktop User_Guide_v2_0.docx -o user.rst
```

We now have a .rst with all the documentation and a folder with all the media assets. 

## Repo setup 

We used the [sphinx-quickstart script](https://www.sphinx-doc.org/en/master/usage/quickstart.html) to get a base repo setup. 

We then copied the user.rst file and the media folder into the "quickstart" folder. 

We then copied this to a docs folder new repo on the BGS GitHub organisation 

## GitHub Pages Setup

To host the documentation on github we need to edit repo settings to enable GitHub pages from gh-pages branch. 

![GitHubPages](../assets/images/2020-02-03-Technical-Documentation/github_setup.png) 

## GitHub Actions Setup

Finally to get this all to work we needed to use GitHub actions to build the HTML from the .rst file to the gh-pages branch. 

This will build each time there's a commit to the master branch using sphinx and the read the docs theme. 

We created ".github/workflows/gh-pages.yml"

```bash
name: github pages

on:
  push:
    branches:
      - master

jobs:
  make-pages:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v1

    - name: select python version
      uses: actions/setup-python@v1
      with:
        python-version: '3.7'

    - name: install dependencies
      run: |
        python -m pip install --upgrade pip
        python -m pip install sphinx
        python -m pip install sphinx_rtd_theme

    - name: build documentation
      run: |
        cd docs
        make html
        touch _build/html/.nojekyll

    - name: deploy
      uses: peaceiris/actions-gh-pages@v2
      env:
        ACTIONS_DEPLOY_KEY: ${{ secrets.ghpagesdk }}
        PUBLISH_BRANCH: gh-pages
        PUBLISH_DIR: docs/_build/html
```

## SSH Setup

To allow GitHub action to modify the repo we need to add SSH keys to repo deploy & repo secrets. 

1. Create SSH keys in Linux/Putty (See Step 1. for example (https://www.digitalocean.com/community/tutorials/how-to-set-up-ssh-keys-on-ubuntu-1604))
2.  In repo settings>deploy add a=deply key such as "ghpagesdk" and copy/paste public key hash
3. In repo settings>secrets add a secret key with same name "ghpagesdk" and copy/paste private key hash. 
4.  make a commit to the master branch and check it's all working ((https://github.com/BritishGeologicalSurvey/Groundhog/actions)). 

![GitHubActions](../assets/images/2020-02-03-Technical-Documentation/Github_Actions.png) 

## Finished

Then (if all's gone to plan) the documention will be available in easy to use format at the repo github pages link - [https://britishgeologicalsurvey.github.io/Groundhog/index.html] 

![GroundHogDocs](../assets/images/2020-02-03-Technical-Documentation/groundhog_docs.png) 

![Screenshot1](../assets/images/2019-11-04-stats/Screenshot1.png)
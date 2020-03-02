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

# Technical Documentation & GitHub Pages


There are known challenges when publishing technical documentation / reports when using PDF or other desktop office formats which is why we endeavor at the BGS to publish our documentation using HTML

GOV.UK has a couple of good blog articles explaining the benefits of publishing to HTML over other formats. 

https://gds.blog.gov.uk/2018/07/16/why-gov-uk-content-should-be-published-in-html-and-not-pdf/

https://phescreening.blog.gov.uk/2016/11/18/bye-bye-pdf-hello-html/

The benefits are such that the Cabinet Office & Government Digital Services specify HTML5 in their guidance for publishing government documents (https://www.gov.uk/government/publications/open-standards-for-government/viewing-government-documents) 

The BGS has been doing this for some time on a number of Projects/Services such as OneGeology & BGS Earthwise, however we hadn't yet done this for some legency documentation such as the user guide for our BGAS GroundHog software (https://www.bgs.ac.uk/research/environmentalModelling/groundhog/groundhogDesktop.html).

With the new release of GroundHog v2.0 we thought it would be a good time to look at migrating the documentation from MS Office/PDF to HTML. 

The solution we came to was based on the workflow of other technical documentation we write at the BGS, namely to use Sphinx (www.sphinx-doc.org) to generate reStructuredText into HTML. 

However we also wanted to be more open in the work that we do, so chose to host the code of GitHub with the documentation website built sing Sphinx via Gitub Actions CI/CD and hosted on GitHub pages 

## Document Conversion  

The GroundHog documentation had already been written MS Word as a .docx 

![word doc](groundhog_word.png "GroundHog Word Doc")

This had to be converted to HTML and the images extracted. 

To do this we used pandoc (https://pandoc.org/), a universal document converter. 

pandoc was installed as explained in it's own documentation.

We than ran the following commands to 1. Convert the text and 2. extract the media/images.  

```bash
pandoc --extract-media=media -s -t rst BGS Groundhog Desktop User Guide v2_0 -o user.rst
```

We now have a .rst with all the documentation and a folder with all the media assets. 

## Repo setup 






To setup 

- follow Sphinx quickstart
- save to GitHub repo
- edit repo settings to enable GitHub pages from gh-pages branch. 
- Create .github/workflows/gh-pages.yml

.. code-block:: bash
		
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
			  
- Create SSH keys in Linux/Putty
- In repo settings>deploy add a=deply key such as "ghpagesdk" and copy/paste public key hash
- In repo settings>secrets add a secret key with same name "ghpagesdk" and copy/paste private key hash. 
- make a commit to the master brach and should all be working. 



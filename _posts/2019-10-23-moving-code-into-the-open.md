---
title:  "Moving code into the open"
author: Dr John A Stevenson
categories:
  - open-source
tags:
  - Python
  - Oracle
  - database
  - GitLab
  - GitHub
  - continuous-integration
---

We recently released our internally-developed [etlhelper](https://github.com/BritishGeologicalSurvey/etlhelper) tool under an open source licence.
This post is a reflection on the experience, explaining what we did and why and with advice for future projects.
The take-home messages are:

+ If the software is intended to be released under an open-source licence, it is simpler to develop it in the open from the start.
+ Developing software in the open is easiest when the surrounding ecosystem is also open source.


## About `etlhelper`

[etlhelper](https://github.com/BritishGeologicalSurvey/etlhelper) is a Python library to simplify data transfer between databases.
We use it where Python programs need to access data in BGS' Oracle (and other) databases.
It is an open source version of software developed internally under the name of `bgs_etl`.

`bgs_etl` began life over a year ago as a script to automate installation of Oracle Instant Client software onto Linux servers and containers.
Later we added functions to simplify connecting to databases and running queries.
Pre-defined connection parameters for internal database servers were also added.
We now use `bgs_etl` in data transfer pipelines and web-service APIs.


## Why release the code?

The UK Government's Digital Services have an excellent blog post describing [The Benefits of Coding in the Open](https://gds.blog.gov.uk/2017/09/04/the-benefits-of-coding-in-the-open/).
These include encouraging the use of best practices and receiving contributions and bug fixes from external users.

`bgs_etl` simplifies generic tasks around running SQL commands via Python so it is useful more widely than just within BGS.
As a developer, it is satisfying to know that your work is helping as many people as possible.
Open-sourcing the code also makes it easy to reuse in projects with external collaborators.


## Steps toward open-sourcing the project

We aimed to publish the source code on the [BGS GitHub repository](https://github.com/BritishGeologicalSurvey) and to upload the Python package to the [PyPI package repository](https://pypi.org/project/etlhelper/) so it can be installed via Python's `pip` command.
There were a number of steps along the way.


### Remove sensitive content

The `bgs_etl` library contained sensitive content such as connection details for BGS databases required for automated tests.
We didn't want to make these public.
Git commands exist to [remove all traces of files](https://help.github.com/en/github/authenticating-to-github/removing-sensitive-data-from-a-repository) from a repository history but we only wanted to remove isolated lines and would still need a new home for the sensitive data.
We decided that the cleanest way to publish the database tools and setup scripts was to move them into a new package, `etlhelper`.
BGS database details remained in our internal `bgs_etl` package, which now imports `etlhelper` as a dependency.

The downside of this approach is that the commit that added 4,800 lines of code from `bgs_etl` took credit for work by multiple authors over the previous year.
This is acknowledged in the [commit message](https://github.com/BritishGeologicalSurvey/etlhelper/commit/8337b9b94bc8c190c28c29077e333a7f320eafe0) but it is small consolation.


### Choose a licence

There are many Open Source licences to choose from; [choosealicence.com](https://choosealicense.com/) has a good summary.
These were new to BGS and so we discussed the various types with the legal department.
In the end, we settled on [GNU LGPLv3](https://choosealicense.com/licenses/lgpl-3.0/).
This makes the code available for commercial and non-commercial use and with no liability on the BGS.
End users are free to modify the code or include it in closed-source packages with the conditions that our contribution must be acknowledged and that any modified versions must be distributed under the same licence.


### Configure repository

_GitLab_ and _GitHub_ are software repository hosting platforms.
BGS runs a _GitLab_ instance on our own server to manage code for internal use.
Even so, we chose to publish `etlhelper` to _GitHub_ as it has a higher profile and we already had a presence there.

Creating a public repository on _GitHub_ for `etlhelper` was straightforward.
However, we also need a version on our internal _GitLab_ server for running our automated tests (see below).
_GitLab_ has a [repository mirroring capability](https://docs.gitlab.com/ee/workflow/repository_mirroring.html#overview) so we configured it to pull in changes from _GitHub_ automatically.
The public-facing _GitHub_ repository now acts as as the definitive source of truth and so project-related tasks, e.g. bug tracking, take place in the open.


### Update Continuous Integration (CI) pipelines

`bgs_etl` had unit and integration tests to ensure that changes to the code didn't break it.
These are run by the Continuous Integration (CI) pipelines.
Unit tests check the logic of individual functions, while integration tests check the software as it would be used.
The integration tests must confirm that `etlhelper` works with Oracle, PostgreSQL, SQLite and MS SQL Server databases.
PostgreSQL and SQLite are open source and test databases can be created at will.
Oracle and MS SQL Server are proprietary and tests must connect to internal BGS servers; they cannot be run from GitHub.

Running at least some tests in GitHub can act as an initial filter and give contributors rapid feedback in the form of a green tick or red cross against their merge request.
Our current solution uses [Travis CI](https://travis-ci.com) to run just the unit tests whenever new code is uploaded.
Once code has been merged it is mirrored down to GitLab where the full test suite is run.
Bad code can still be merged, but we will not make a 'release' and upload it to PyPI unless all the tests have passed in GitLab.
External contributers can be notified via a comment on their merge request.

Soon we will add PostgreSQL and SQLite integration tests to Travis.
This is possible because the test suite was refactored to cleanly separate the different database types.
Test database parameters are defined by environment variables (and therefore not stored in the code) and tests for a given database type are automatically skipped if the database is unreachable.
As a result, the main application logic will be covered by tests that run in GitHub and only tests specific to different proprietary database types will depend on GitLab.


## Thoughts on how things went

Coding in the open is a new way of working for BGS and this project represents
a test-case.
Hopefully it will be the first example of many.
Getting initial sign-off for the release took longer than expected as there was
no clear 'category' for this kind of output.
Was it a product?  A publication?  A dataset?  Should it have a DOI?

It is hard to tell how `etlhelper` has been received in the month since it was released.
We have received neither pull requests with amazing new features (😞) nor bug reports (😊) so far.
By making the code open we can track [Stars](https://github.com/BritishGeologicalSurvey/etlhelper/stargazers), [Forks](https://github.com/BritishGeologicalSurvey/etlhelper/network/members) and [downstream dependents](https://github.com/BritishGeologicalSurvey/etlhelper/network/dependents) on GitHub, and [PyPI stats](https://pypistats.org/packages/etlhelper) records monthly downloads.
These are quantitative measures that can be used to track "impact".

Splitting `etlhelper` out of `bgs_etl` was a major refactor of the code.
This would have been torture without a suite of tests to confirm that it all still worked.
It was a shame to lose the commit history when we transferred the repository.
It wouldn't have happened if we had been developing on GitHub from the beginning.
This is a lesson for future projects that are likely to be open-sourced.

Maintaining two CI pipelines adds effort to the project but is unavoidable in this case because we need to test against proprietary databases.
On the other hand, it is good to know that we can trigger internal CI jobs from
code hosted externally.
More generally, it demonstrates that developing software in the open is easier if the surrounding ecosystem is also open source.

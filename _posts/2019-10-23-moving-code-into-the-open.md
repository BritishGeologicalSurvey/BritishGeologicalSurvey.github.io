# Moving code into the open

We recently released our internally-developed [etlhelper](https://github.com/BritishGeologicalSurvey/etlhelper) tool under an open source licence.
This post is a reflection on the experience, explaining what we did and why and
with advice for future projects.
The take-home messages are:

+ If the software is intended to be released under an open-source licence, it
  is simpler to develop it in the open from the start
+ Developing software in the open is easiest when the surrounding ecosystem is
  also open source


## About `etlhelper`

[etlhelper](https://github.com/BritishGeologicalSurvey/etlhelper) is a Python
library to simplify data transfer between databases.
We use it where Python programs need to access data in BGS' Oracle (and other) databases.
It is an open source version of software developed internally under the name of
`bgs_etl`.


`bgs_etl` began life as a script to automate installation of Oracle Instant
Client software onto Linux servers and containers.
Later we added functions to simplify connecting to databases and running
queries.
Pre-defined connection parameters for internal database servers were also added.
Over the past year it has been incorporated into data transfer pipelines and
web-service APIs.


## Why release the code?

The UK Government's Digital Services have an excellent blog post describing
[The Benefits of Coding in the Open](https://gds.blog.gov.uk/2017/09/04/the-benefits-of-coding-in-the-open/).
These include encouraging the use of best practices and receiving contributions
and bug fixes from external users.

For me, the most important reasons were that the work was tax-payer funded so I
wanted as many people as possible to benefit from it, and because open-sourcing
the code makes it easy to reuse in projects with external collaborators.
The core functions of `bgs_etl` simplified generic tasks around running SQL
commands via Python so they are useful more widely than just within BGS.


## Steps toward open-sourcing the project


We aimed to publish the source code on the [BGS GitHub repository](https://github.com/BritishGeologicalSurvey) and to upload the Python package to the [PyPI package repository](https://pypi.org/project/etlhelper/) so it can be installed via Python's `pip` command.
There were a number of steps along the way.


### Remove sensitive content

The `bgs_etl` library contained sensitive content such as connection details
for BGS databases that we didn't want to publish.
Integration tests depended on our internal Oracle database, too.
We decided that the cleanest solution was to split the database tools and setup scripts were moved into a new `etlhelper` package.
Things like BGS database details remained in our internal `bgs_etl`
package, which now imports `etlhelper` as a dependency.

There are Git commands that can modify your repository to remove files that
only existed in past commits but in this case it was cleaner to start with a
fresh repository.
The big disadvantage here is that the commit that added 4,800 lines of code
from `bgs_etl` got all the credit for work by multiple authors over the
previous year.
This is acknowledged in the [commit
message](https://github.com/BritishGeologicalSurvey/etlhelper/commit/8337b9b94bc8c190c28c29077e333a7f320eafe0)
but it is small consolation.


### Choose a licence

There a many Open Source licences to choose from - [choosealicence.com](https://choosealicense.com/) has a good summary.
These were new to BGS and so we discussed the various types with the legal
department.
In the end, we settled on [GNU
LGPLv3](https://choosealicense.com/licenses/lgpl-3.0/).
This makes the code available for commercial and non-commercial use and with no
liability on the BGS.
End users are free to modify the code or include it in closed-source packages
with the condition that any modified versions must be distributed under the
same licence.


### Configure repository

BGS has an self-hosted GitLab instance to manage code for internal use, but we
chose to publish the public `etlhelper` to GitHub as it has a higher profile
and we already had a presence there.

Creating a public repository on _GitHub_ for `etlhelper` was straightforward,
however we also needed to maintain a version on _GitLab_ server.
This was required for the Continuous Integration (CI) system that automatically runs
tests on the code when changes are made (see below).
We used GitLab's [repository mirroring
capability](https://docs.gitlab.com/ee/workflow/repository_mirroring.html#overview)
that pulls in changes from GitHub automatically.
This way we could use the public GitHub repository as the definitive source of
truth and all tools such as bug tracking would be fully visible to the public.


### Update Continuous Integration (CI) pipelines

`bgs_etl` had unit and integration tests to ensure that changes to the code
didn't break it.
Unit tests check the logic of individual functions, while integration tests
check the software as it would be used.
The integration tests connected to our internal Oracle and MS SQL
Server databases as the whole point of the software was to make it easier to
work with these databases.
They also connect to an (open-source) PostgreSQL database that is created in a
Docker container specifically for the tests and destroyed again afterwards.
Internally, these were run by GitLab's CI tools.

Moving to GitHub presented problems because those database connections are not
available outside BGS.
Nevertheless, we still wanted automatic tests to run there.
Our initial solution is to use [Travis CI](https://travis-ci.com) to run the
just the unit tests for merge requests made in GitHub as an initial filter.
The full test-suite is automatically run by GitLab once code has been merged
and synchronised by the mirroring service.
This doesn't stop bad code being merged, but we will not make a 'release' and
upload it to PyPI unless all the tests have passed in GitLab.

The integration tests were refactored to cleanly separate the different
database types.
This will allow integration tests for PostgreSQL and SQLite only to run in Travis CI
as well.
These are open source databases so we can create and destroy instances as
required.
Once this is configured, all the connection and data transfer logic will be
covered in public-facing tests leaving just database-specific issues to be
caught by the internal GitLab test runs.


## Thoughts on how things went

Coding in the open is a new way of working for BGS and this project represents
a test-case.
Hopefully it will be the first example of many.
Getting initial sign-off for the release took longer than expected as there was
no clear 'category' for this kind of output.
Was it a product?  A publication?  A dataset?  Should it have a DOI?

The code has only been out for a month and the flood of pull requests from
external contributors racing to make improvements to our code has yet to arrive.
By making the code open we can track we can track [Stars](https://github.com/BritishGeologicalSurvey/etlhelper/stargazers), [Forks](https://github.com/BritishGeologicalSurvey/etlhelper/network/members) and
[downstream dependents](https://github.com/BritishGeologicalSurvey/etlhelper/network/dependents) on GitHub, and [PyPI
stats](https://pypistats.org/packages/etlhelper) records monthly downloads.
These provide cold, hard metrics that can be used to quantify the 'impact' of
releasing `etlhelper` into the wild, and will reveal if others find it useful.

It was a shame to lose the commit history when we transferred the repository.
If we had been developing on GitHub from the beginning, this wouldn't have
happened.
This is a lesson for future projects that are likely to be open-sourced.

Similarly, disentangling the CI pipeline turned out to be lots of work.
If a project is developed in the open from the beginning then the pipeline
wouldn't need to be changed.
In our case, we would still need duplicate pipelines in order to connect to our
Oracle and MS SQL Server databases.
We have a satisfactory solution now, but these types of automated, Infrastructure-as-Code workflows are much easier when the whole ecosystem is based on open source tools.

